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
        goldcount = connection.execute(sqlalchemy.text("SELECT SUM(change) AS gold FROM gold_ledgers")).fetchone()[0]
        if (goldcount > 0):
            connection.execute(
                    sqlalchemy.text("INSERT INTO gold_ledgers (change) VALUES (:change)"),
                    {"change": -(goldcount)})
        if(goldcount < 0):
            connection.execute(
                    sqlalchemy.text("INSERT INTO gold_ledgers (change) VALUES (:change)"),
                    {"change": (goldcount)})
                
        # setting all potion_ledgers to 0
        connection.execute(sqlalchemy.text("UPDATE potion_ledgers SET change = 0"))
        # mls back to 0

        connection.execute(sqlalchemy.text("UPDATE ml_ledgers SET red_ml = 0, blue_ml = 0, green_ml = 0, dark_ml = 0"))
        
    return "OK"

