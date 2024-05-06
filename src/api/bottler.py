from fastapi import APIRouter, Depends
from enum import Enum
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/bottler",
    tags=["bottler"],
    dependencies=[Depends(auth.get_api_key)],
)


class PotionInventory(BaseModel):
    potion_type: list[int]
    quantity: int

@router.post("/deliver/{order_id}")
def post_deliver_bottles(potions_delivered: list[PotionInventory], order_id: int):
    """ 
    subtract right amount of ml, add right amount of potions
    NO HARDCODING: 
    if potion_type (RGBD) IN potions database 
    """
    
    with db.engine.begin() as connection:
    
        for i in range(len(potions_delivered)):
            added_potions = potions_delivered[i].quantity
            potion_type = potions_delivered[i].potion_type

            result = connection.execute(sqlalchemy.text("SELECT * FROM potions WHERE red = :red AND green = :green AND blue = :blue AND dark = :dark"),
                {"red": potion_type[0], "green": potion_type[1], "blue": potion_type[2], "dark": potion_type[3]})
            row = result.fetchone()

            if (row):
                sku = row[1]
                potion_id = row.id
                
                if (potion_type[0] > 0):
                    ###LEDGER
                    connection.execute(sqlalchemy.text("INSERT INTO ml_ledgers (red_ml) VALUES (:red_ml)"),
                    {"red_ml": -(potion_type[0])* added_potions}
                    )
                
                if (potion_type[1] > 0):
                    ###LEDGER
                    connection.execute(sqlalchemy.text("INSERT INTO ml_ledgers (green_ml) VALUES (:green_ml)"),
                    {"green_ml": -(potion_type[1]) *added_potions}
                    )

                if (potion_type[2] > 0):
                    ###LEDGER
                    connection.execute(sqlalchemy.text("INSERT INTO ml_ledgers (blue_ml) VALUES (:blue_ml)"),
                    {"blue_ml": -(potion_type[2])*added_potions}
                    )

                if (potion_type[3] > 0):
                    ###LEDGER
                    connection.execute(sqlalchemy.text("INSERT INTO ml_ledgers (dark_ml) VALUES (:dark_ml)"),
                    {"dark_ml": -(potion_type[3])*added_potions}
                    )

               ###LEDGER -- note, I will eventually not need endpoint above because I can SUM all deltas in potions_ledgers where id is potion_id
                connection.execute(sqlalchemy.text("INSERT INTO potion_ledgers (potion_id, change) VALUES (:potion_id, :change)"),
                    {"potion_id": potion_id, "change": (added_potions)}
                    )


    print(f"potions delievered: {potions_delivered} order_id: {order_id}")

    return "OK"

@router.post("/plan")
def get_bottle_plan():
    """
    Go from barrel to bottle.
    """

    # Each bottle has a quantity of what proportion of red, blue, and
    # green potion to add.
    # Expressed in integers from 1 to 100 that must sum up to 100.

    # Initial logic: bottle all barrels into red potions.

    # see how much ml we have in our global inventory
    with db.engine.begin() as connection:
        redml = connection.execute(sqlalchemy.text("SELECT SUM(red_ml) AS red_ml FROM ml_ledgers")).fetchone()[0] 
        greenml = connection.execute(sqlalchemy.text("SELECT SUM(green_ml) AS green_ml FROM ml_ledgers")).fetchone()[0] 
        blueml = connection.execute(sqlalchemy.text("SELECT SUM(blue_ml) AS blue_ml FROM ml_ledgers")).fetchone()[0] 
        darkml = connection.execute(sqlalchemy.text("SELECT SUM(dark_ml) AS dark_ml FROM ml_ledgers")).fetchone()[0] 
    
        potions = connection.execute(sqlalchemy.text("SELECT * from potions"))

        # eventually, sum up cols

        output = []

        for potion in potions:
            print(potion)
            make_with_blue = make_with_dark = make_with_green = make_with_red = 1000 # initialize
            # dont div by 0
            if(potion.red != 0):
                make_with_red = redml // potion.red
            if(potion.green != 0):
                make_with_green = greenml // potion.green
            if(potion.blue != 0):
                make_with_blue = blueml // potion.blue
            if(potion.dark != 0):
                make_with_dark = darkml // potion.dark

            potions_can_make = min(make_with_red, make_with_green, make_with_blue, make_with_dark)
            
            # if 50 red and 100 green, can still just make one yellow potion.
            lst = [potion.red, potion.green, potion.blue, potion.dark]
            if(potions_can_make > 0):
                output.append({
                "potion_type": lst,
                "quantity": potions_can_make
                })
            
            redml -= potions_can_make * potion[2]
            greenml -= potions_can_make * potion[3]
            blueml -= potions_can_make * potion[4]
            darkml -= potions_can_make * potion[5]

        return output


if __name__ == "__main__":
    print(get_bottle_plan())