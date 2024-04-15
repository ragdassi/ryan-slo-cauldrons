from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src.api import auth
from src import database as db
import sqlalchemy

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(auth.get_api_key)],
)

@router.post("/reset")
def reset():
    """
    Reset the game state. Gold goes to 100, all potions are removed from
    inventory, and all barrels are removed from inventory. Carts are all reset.
    """

    with db.engine.begin() as connection:
        # Set gold back to 100
        connection.execute(sqlalchemy.text("UPDATE global_inventory SET gold = :gold"),
                    {"gold": 100})
        #set inventory back to 0

        # num potions back to 0
        connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_green_potions = :num_green_potions, num_blue_potions = :num_blue_potions, num_red_potions = :num_red_potions"),
                    {"num_green_potions": 0, "num_blue_potions": 0, "num_red_potions": 0})
        
        # mls back to 0
        connection.execute(sqlalchemy.text("UPDATE global_inventory SET millileters = :millileters, green_ml = :green_ml, red_ml = :red_ml, blue_ml = :blue_ml"),
                    {"millileters": 0, "green_ml": 0, "red_ml": 0,  "blue_ml": 0})
        
    return "OK"

