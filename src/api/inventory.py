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
        
        sum = connection.execute(sqlalchemy.text("SELECT SUM(quantity) AS total_quantity FROM potions")).fetchone()  
        total_quantity = sum[0]
        
    total_ml = greenml + redml + blueml + darkml

    return {"gold": gold_sum_result, "Number of potions": total_quantity, "total_millileters": total_ml}

# Gets called once a day
@router.post("/plan")
def get_capacity_plan():
    """ 
    Start with 1 capacity for 50 potions and 1 capacity for 10000 ml of potion. Each additional 
    capacity unit costs 1000 gold.
    """

    return {
        "potion_capacity": 0,
        "ml_capacity": 0
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

    return "OK"
