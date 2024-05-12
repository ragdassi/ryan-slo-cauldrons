from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import math
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/inventory",
    tags=["inventory"],
    dependencies=[Depends(auth.get_api_key)],
)

@router.get("/audit")
def get_inventory():
    """ """
    with db.engine.begin() as connection:
        greenml = connection.execute(sqlalchemy.text("SELECT SUM(green_ml) AS green_ml FROM ml_ledgers")).fetchone()[0] 
        redml = connection.execute(sqlalchemy.text("SELECT SUM(red_ml) AS red_ml FROM ml_ledgers")).fetchone()[0] 
        blueml = connection.execute(sqlalchemy.text("SELECT SUM(blue_ml) AS blue_ml FROM ml_ledgers")).fetchone()[0] 
        darkml = connection.execute(sqlalchemy.text("SELECT SUM(dark_ml) AS dark_ml FROM ml_ledgers")).fetchone()[0] 
    
        gold_sum_result = connection.execute(sqlalchemy.text("SELECT SUM(change) AS gold FROM gold_ledgers")).fetchone()[0]
        sum = connection.execute(sqlalchemy.text("SELECT SUM(change) AS change FROM potion_ledgers")).fetchone()  
        
        if(sum):
            total_quantity = sum[0]
        else:
            total_quantity = 0
        
    total_ml = greenml + redml + blueml + darkml

    return {"gold": gold_sum_result, "Number of potions": total_quantity, "total_millileters": total_ml}

# Gets called once a day
@router.post("/plan")
def get_capacity_plan():
    """ 
    Start with 1 capacity for 50 potions and 1 capacity for 10000 ml of potion. Each additional 
    capacity unit costs 1000 gold.
    """
   
    with db.engine.begin() as connection:
        # what is current capacity
        cur_potion_cap = connection.execute(sqlalchemy.text("SELECT SUM(potions_cap_change) AS current_potions_capacity FROM cap_ledger")).fetchone()[0]
        cur_ml_cap = connection.execute(sqlalchemy.text("SELECT SUM(ml_cap_change) AS current_ml_capacity FROM cap_ledger")).fetchone()[0]
        
        # what is current gold
        gold = connection.execute(sqlalchemy.text("SELECT SUM(change) AS gold FROM gold_ledgers")).fetchone()[0]
        potion_capacity = ml_capacity = 0

        if gold > 1000 and cur_potion_cap  < 5:
            potion_capacity = 1
            gold -= 1000
            connection.execute(
                    sqlalchemy.text("INSERT INTO gold_ledgers (change) VALUES (:change)"),
                    {"change": -(1000)}
                )

        if gold > 1000 and cur_ml_cap < 10:
            ml_capacity = 1
            connection.execute(
                    sqlalchemy.text("INSERT INTO gold_ledgers (change) VALUES (:change)"),
                    {"change": -(1000)}
                )
        
    
    return {
        "potion_capacity": potion_capacity,
        "ml_capacity": ml_capacity
        }

class CapacityPurchase(BaseModel):
    potion_capacity: int
    ml_capacity: int

# Gets called once a day
@router.post("/deliver/{order_id}")
def deliver_capacity_plan(capacity_purchase : CapacityPurchase, order_id: int):
    """ 
    Start with 1 capacity for 50 potions and 1 capacity for 10000 ml of potion. Each additional 
    capacity unit costs 1000 gold.
    """
    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text("INSERT INTO cap_ledger (ml_cap_change, potions_cap_change) VALUES (:ml_cap_change, :potions_cap_change)"),
            {"ml_cap_change": capacity_purchase.ml_capacity, "potions_cap_change": capacity_purchase.potion_capacity}
        )

    return "OK"
