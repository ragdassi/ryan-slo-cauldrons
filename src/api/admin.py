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
        connection.execute(sqlalchemy.text("TRUNCATE TABLE gold_ledgers"))
        connection.execute(
                    sqlalchemy.text("INSERT INTO gold_ledgers (change) VALUES (:change)"),
                    {"change": 100}
                )
        # setting all potion_ledgers to 0
        connection.execute(sqlalchemy.text("TRUNCATE TABLE potion_ledgers"))
        # mls back to 0

        connection.execute(sqlalchemy.text("TRUNCATE TABLE ml_ledgers"))
    return "OK"

