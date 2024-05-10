from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from sqlalchemy.sql import func
from sqlalchemy import text
from src import database as db

router = APIRouter(
    prefix="/barrels",
    tags=["barrels"],
    dependencies=[Depends(auth.get_api_key)],
)

class Barrel(BaseModel):
    sku: str

    ml_per_barrel: int
    potion_type: list[int]
    price: int

    quantity: int

@router.post("/deliver/{order_id}")
def post_deliver_barrels(barrels_delivered: list[Barrel], order_id: int):
    """ 
    only have one barrel over here 
    based on order id, 

    with db engine begin connection, try connection execute sqlalchemy(inser into processed (job id, type) VALUES (:order_id, 'barrels'), 
    {"order_id": orderid})
    execpt integrity error as e, return ok

    ^ allows code to be retryable

    sole job is in updating the DB


    """
   

    with db.engine.begin() as connection:
        for barrel in barrels_delivered:
            subtracted_gold = barrel.price * barrel.quantity
            added_ml = barrel.ml_per_barrel * barrel.quantity
            print(barrel.potion_type)

            # Green
            if(barrel.potion_type == [0, 1, 0, 0]):
                
             ###LEDGER
                connection.execute(
                    sqlalchemy.text("INSERT INTO gold_ledgers (change) VALUES (:change)"),
                    {"change": -(subtracted_gold)}
                )
                ###LEDGER
                connection.execute(
                    sqlalchemy.text("INSERT INTO ml_ledgers (green_ml) VALUES (:green_ml)"),
                    {"green_ml": (added_ml)}
                )
            
            # Red
            if(barrel.potion_type == [1, 0, 0, 0]):
              
                ###LEDGER
                connection.execute(
                        sqlalchemy.text("INSERT INTO gold_ledgers (change) VALUES (:change)"),
                        {"change": -(subtracted_gold)}
                    )
                ###LEDGER
                connection.execute(
                    sqlalchemy.text("INSERT INTO ml_ledgers (red_ml) VALUES (:red_ml)"),
                    {"red_ml": (added_ml)}
                )

            
            # BLUE
            if(barrel.potion_type == [0, 0, 1, 0]):
               
                ###LEDGER
                connection.execute(
                    sqlalchemy.text("INSERT INTO gold_ledgers (change) VALUES (:change)"),
                    {"change": -(subtracted_gold)}
                )
                ###LEDGER
                connection.execute(
                    sqlalchemy.text("INSERT INTO ml_ledgers (blue_ml) VALUES (:blue_ml)"),
                    {"blue_ml": (added_ml)}
                )
            
            #DARK
            if(barrel.potion_type == [0, 0, 0, 1]):
    
                ###LEDGER
                connection.execute(
                    sqlalchemy.text("INSERT INTO gold_ledgers (change) VALUES (:change)"),
                    {"change": -(subtracted_gold)}
                )
                ###LEDGER
                connection.execute(
                    sqlalchemy.text("INSERT INTO ml_ledgers (dark_ml) VALUES (:dark_ml)"),
                    {"dark_ml": (added_ml)}
                )
        
    print(f"barrels delievered: {barrels_delivered} order_id: {order_id}")

    return "OK"

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ 
    loop through the barrels roxanne offering, only do accept if its green

    find cheapest barrel to replensih stock - only do so if im past a threshold

    else gold, potion_type, MAX_ML - currentml)
    """
    with db.engine.begin() as connection:
        gold = connection.execute(sqlalchemy.text("SELECT SUM(change) AS gold FROM gold_ledgers")).fetchone()[0]
        print(gold)
    gold_count = 0
    quant = 0
    barrel_plan = []
    for i in range(len(wholesale_catalog)):
        if(wholesale_catalog[i].potion_type == [1, 0, 0, 0] or [0, 1, 0, 0] or [0, 0, 1, 0] or [0, 0, 0, 1]):
            if (wholesale_catalog[i].price + gold_count <= gold):
                quant += 1
                barrel_plan.append({
                    "sku": wholesale_catalog[i].sku,
                    "quantity": 1
                })
                gold_count += wholesale_catalog[i].price

    return barrel_plan
                

