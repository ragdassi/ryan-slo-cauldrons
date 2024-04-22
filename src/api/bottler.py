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
    """
    
    with db.engine.begin() as connection:
        subtracted_ml = 0

        # for potion in potions_delivered:
        for i in range(len(potions_delivered)):
            added_potions = potions_delivered[i].quantity
            potion_type = potions_delivered[i].potion_type
            # note = subtracting 100 ML per bottle

            # GREEN POTION
            if(potion_type == [0, 100, 0, 0]):
                connection.execute(sqlalchemy.text("UPDATE global_inventory SET green_ml = green_ml - :green_ml, num_potions = num_potions + :num_potions"),
                {"green_ml": 100, "num_potions":added_potions}) 

                connection.execute(sqlalchemy.text("UPDATE potions SET quantity = quantity + :quantity WHERE sku = 'GREENPOTION'"),
                {"quantity":added_potions})

            # BLUE POTION
            if(potion_type == [0, 0, 100, 0]):
                connection.execute(sqlalchemy.text("UPDATE global_inventory SET blue_ml = blue_ml - :blue_ml, num_potions = num_potions + :num_potions"),
                {"blue_ml": 100, "num_potions":added_potions})

                connection.execute(sqlalchemy.text("UPDATE potions SET quantity = quantity + :quantity WHERE sku = 'BLUEPOTION'"),
                {"quantity":added_potions})
            
            # RED POTION
            if(potion_type == [100, 0, 0, 0]):
                connection.execute(sqlalchemy.text("UPDATE global_inventory SET red_ml = red_ml - :red_ml, num_potions = num_potions + :num_potions"),
                {"red_ml": 100, "num_potions":added_potions,})

                connection.execute(sqlalchemy.text("UPDATE potions SET quantity = quantity + :quantity WHERE sku = 'REDPOTION'"),
                {"quantity":added_potions})
            

            # DARK POTION
            if(potion_type == [0, 0, 0, 100]):
                connection.execute(sqlalchemy.text("UPDATE global_inventory SET dark_ml = dark_ml - :dark_ml, num_potions = num_potions + :num_potions"),
                {"dark_ml": 100, "num_potions":added_potions})

                connection.execute(sqlalchemy.text("UPDATE potions SET quantity = quantity + :quantity WHERE sku = 'DARKPOTION'"),
                {"quantity":added_potions})

            # PURPLE POTION
            if(potion_type == [50, 0, 50, 0]):
                connection.execute(sqlalchemy.text("UPDATE global_inventory SET red_ml = red_ml - :red_ml, blue_ml = blue_ml - :blue_ml, num_potions = num_potions + :num_potions"),
                {"red_ml": 50, "blue_ml": 50, "num_potions": added_potions})

                connection.execute(sqlalchemy.text("UPDATE potions SET quantity = quantity + :quantity WHERE sku = 'PURPLEPOTION'"),
                {"quantity":added_potions})
            
            # BROWN POTION
            if(potion_type == [50, 50, 0, 0]):
                connection.execute(sqlalchemy.text("UPDATE global_inventory SET red_ml = red_ml - :red_ml, green_ml = green_ml - :green_ml, num_potions = num_potions + :num_potions"),
                {"red_ml": 50, "green_ml": 50, "num_potions": added_potions})

                connection.execute(sqlalchemy.text("UPDATE potions SET quantity = quantity + :quantity WHERE sku = 'BROWNPOTION'"),
                {"quantity":added_potions})
            
            # TURQOISE POTION
            if(potion_type == [0, 50, 50, 0]):
                connection.execute(sqlalchemy.text("UPDATE global_inventory SET blue_ml = blue_ml - :blue_ml, green_ml = green_ml - :green_ml, num_potions = num_potions + :num_potions"),
                {"blue_ml": 50, "green_ml": 50, "num_potions": added_potions})

                connection.execute(sqlalchemy.text("UPDATE potions SET quantity = quantity + :quantity WHERE sku = 'TURQUOISEPOTION'"),
                {"quantity":added_potions})

            # BLOOD POTION
            if(potion_type == [50, 0, 0, 50]):
                connection.execute(sqlalchemy.text("UPDATE global_inventory SET red_ml = red_ml - :red_ml, dark_ml = dark_ml - :dark_ml, num_potions = num_potions + :num_potions"),
                {"red_ml": 50, "dark_ml": 50, "num_potions": added_potions})

                connection.execute(sqlalchemy.text("UPDATE potions SET quantity = quantity + :quantity WHERE sku = 'BLOODPOTION'"),
                {"quantity":added_potions})


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
        redml = connection.execute(sqlalchemy.text("SELECT red_ml from global_inventory")).fetchone()[0] 
        greenml = connection.execute(sqlalchemy.text("SELECT green_ml from global_inventory")).fetchone()[0] 
        blueml = connection.execute(sqlalchemy.text("SELECT blue_ml from global_inventory")).fetchone()[0] 
        darkml = connection.execute(sqlalchemy.text("SELECT dark_ml from global_inventory")).fetchone()[0] 
    output = []

    redpotions = redml // 100
    greenpotions = greenml // 100
    bluepotions = blueml // 100
    darkpotions = darkml // 100

    print(redpotions, greenpotions, bluepotions, darkpotions)
    
    if (redpotions > 0 and bluepotions > 0):
        # add a red
        output.append(
            {
                "potion_type": [50, 0, 50, 0],
                "quantity": redpotions,
            }
        )
    if (greenpotions > 0):
         output.append(
            {
                "potion_type": [0, 100, 0, 0],
                "quantity": greenpotions,
            }
        )
    if (bluepotions > 0):
        output.append(
                {
                    "potion_type": [0, 0, 100, 0],
                    "quantity": bluepotions,
                }
        )

    print(output)
    return output
        

if __name__ == "__main__":
    print(get_bottle_plan())