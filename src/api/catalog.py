from fastapi import APIRouter
import sqlalchemy
from src import database as db

router = APIRouter()


@router.get("/catalog/", tags=["catalog"])
def get_catalog():
    """
    retrieve data from supabase - related to getstarted pseudocode - 
    Each unique item combination must have only a single price.

    fetch - get row, get numbering potions variable. if > 0, make it 1 just for now. return hard coded data.  
    """
    catalogs = []
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("SELECT * FROM global_inventory")).fetchone()
    
        if result[0] > 0:
            return [
            {
                "sku": "GREEN_POTION_0",
                "name": "green potion",
                "quantity": 1,
                "price": 50,
                "potion_type": [0, 1, 0, 0],
            }
        ]
        else:
            return []
    
   

    
