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
        result = connection.execute(
            sqlalchemy.text("SELECT potion_id, COALESCE(SUM(change), 0) AS total_change "
                            "FROM potion_ledgers "
                            "GROUP BY potion_id")
        ).fetchall()
        
        print(result)
        
        for row in result:
            potion_id = row.potion_id
            total_change = row.total_change or 0
            
            if total_change != 0:
                potion_info = connection.execute(
                    sqlalchemy.text("SELECT sku, red, green, blue, dark, price FROM potions WHERE id = :id"),
                    {"id": potion_id}
                ).fetchone()

                catalog.append({
                    "sku": potion_info.sku,
                    "quantity": total_change,  # Use total_change as the quantity
                    "potion_type": [potion_info.red, potion_info.green, potion_info.blue, potion_info.dark],
                    "price": potion_info.price
                })
    return catalog

    
