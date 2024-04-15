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
            subtracted_gold = barrel.price * barrel.quantity
            added_ml = barrel.ml_per_barrel * barrel.quantity

            # Green
            if(barrel.potion_type == [0, 1, 0, 0]):
                connection.execute(
                    sqlalchemy.text("UPDATE global_inventory SET gold = gold - :gold, green_ml = green_ml + :green_ml"),
                    {"gold": subtracted_gold, "green_ml": added_ml})  # ML??
            # Red
            if(barrel.potion_type == [1, 0, 0, 0]):
                connection.execute(
                    sqlalchemy.text("UPDATE global_inventory SET gold = gold - :gold, red_ml = red_ml + :red_ml"),
                    {"gold": subtracted_gold, "red_ml": added_ml})  # ML??
            # BLUE
            if(barrel.potion_type == [0, 0, 1, 0]):
                connection.execute(
                    sqlalchemy.text("UPDATE global_inventory SET gold = gold - :gold, blue_ml = blue_ml + :blue_ml"),
                    {"gold": subtracted_gold, "blue_ml": added_ml})  # ML??

        
    print(f"barrels delievered: {barrels_delivered} order_id: {order_id}")

    return "OK"

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ 
    loop through the barrels roxanne offering, only do accept if its green
    """
    with db.engine.begin() as connection:
        gold = connection.execute(sqlalchemy.text("SELECT gold FROM global_inventory")).fetchone()[0] # tuple is size 1 
    gold_count = 0
    quant = 0
    skus = []
    for i in range(len(wholesale_catalog)):
        if(wholesale_catalog[i].potion_type == [1, 0, 0, 0] or [0, 1, 0, 0] or [0, 0, 1, 0]):
            if (wholesale_catalog[i].price + gold_count <= gold):
                skus.append(wholesale_catalog[i].sku)
                gold_count += wholesale_catalog[i].price
                quant += 1
                

    if ((quant > 0) and len(skus) > 0):
        to_add = {
            "sku": skus,
            "quantity": quant
        }
        return [
            to_add
        ]
    else:
        return []
                

