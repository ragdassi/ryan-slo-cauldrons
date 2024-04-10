from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
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
    """
    if len(barrels_delivered) != 1:
        return {"error": "Only one barrel can be delivered per order."}, 400

    with db.engine.begin() as connection:
        for barrel in barrels_delivered:
            subtracted_gold = barrel.price
            added_ml = barrel.ml_per_barrel
         
        connection.execute(
            sqlalchemy.text("UPDATE global_inventory SET gold = gold - :gold, millileters = millileters + :millileters"),
            {"gold": subtracted_gold, "millileters": added_ml, "inventory_id":barrel.sku})  # ML??

    # result is whole table. 

        #if result is good, rturn it
        # subtract gold, add ml
    
    print(f"barrels delievered: {barrels_delivered} order_id: {order_id}")

    return "OK"

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ 
    loop through the barrels roxanne offering, only do accept if its green
    """
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("SELECT gold FROM global_inventory")).fetchone()[0] # tuple is size 1 
    possible_green_barrels = []
    gold_count = 0
    quant = 0
    for i in range(len(wholesale_catalog)):
        if(wholesale_catalog[i].potion_type == "SMALL_GREEN_BARREL"):
            if (wholesale_catalog[i].price + gold_count <= result[0]):
                print(result[0])
                gold_count += wholesale_catalog[i].price
                quant += 1

    if (quant > 0):
        to_add = {
            "sku": "SMALL_GREEN_BARREL",
            "quantity": quant
        }
        return [
            to_add
        ]
    else:
        return []
                
    # possible_green_barrels.append(row)
            
    
    # if num I want to buy is 0, return empty list

