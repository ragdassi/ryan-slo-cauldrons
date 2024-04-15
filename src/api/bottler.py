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
    # dummy data - hardcoded
    potion_ml_map = {
    "potion_type_1": 100,  
    "potion_type_2": 150,  
    }
    with db.engine.begin() as connection:
        subtracted_ml = 0

        for potion in potions_delivered:
            added_potions = potion.quantity
            potion_type = potion.potion_type

            
            ml_per_potion = potion_ml_map.get(potion_type, 0)
            subtracted_ml = ml_per_potion * added_potions

            if(potion.potion_type == [1, 0, 0, 0]):
                result = connection.execute(sqlalchemy.text("UPDATE global_inventory SET red_ml = red_ml - :red_ml, numpotions = numpotions + :numpotions"),
                {"red_ml": subtracted_ml, "quantity":added_potions})  # ML??))

            if(potion.potion_type == [0, 1, 0, 0]):
                result = connection.execute(sqlalchemy.text("UPDATE global_inventory SET green_ml = green_ml - :green_ml, numpotions = numpotions + :numpotions"),
                {"green_ml": subtracted_ml, "quantity":added_potions})  # ML??))
            if(potion.potion_type == [0, 0, 1, 0]):
                result = connection.execute(sqlalchemy.text("UPDATE global_inventory SET blue_ml = blue_ml - :blue_ml, numpotions = numpotions + :numpotions"),
                {"blue_ml": subtracted_ml, "quantity":added_potions})  # ML??))
                
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
        totalml = connection.execute(sqlalchemy.text("SELECT millileters from global_inventory")).fetchone()[0] 
        redml = connection.execute(sqlalchemy.text("SELECT red_ml from global_inventory")).fetchone()[0] 
        greenml = connection.execute(sqlalchemy.text("SELECT green_ml from global_inventory")).fetchone()[0] 
        blueml = connection.execute(sqlalchemy.text("SELECT blue_ml from global_inventory")).fetchone()[0] 
    output = []
    
    while (totalml > 0):
        # TODO - logic for checking if ml color is zero. why add if theres none of a particular color?
        output.append(
            {
                "potion_type": [100, 0, 0, 0],
                "quantity": 1,
            }
        )
        if (totalml - redml < 0):
            break
        else:
            totalml -= redml
        
        output.append(
            {
                "potion_type": [0, 100, 0, 0],
                "quantity": 1,
            }
        )
        
        if (totalml - greenml < 0):
            break
        else:
            totalml -= greenml
        
        output.append(
            {
                "potion_type": [0, 0, 100, 0],
                "quantity": 1,
            }
        )
        if (totalml - blueml < 0):
            break
        else:
            totalml -= blueml
    
    

    # returning 5 red potions
    return output
        

if __name__ == "__main__":
    print(get_bottle_plan())