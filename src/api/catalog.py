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
    catalog = []
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("SELECT inventory, sku, type, price from potion_catalog")).all()

        for row in result:
            catalog.append({"sku": row.sku, "quantity": row.inventory, "potion_type": row.type, "price": row.price})
    
    return catalog

    
