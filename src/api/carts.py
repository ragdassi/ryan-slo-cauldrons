from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src.api import auth
from enum import Enum
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/carts",
    tags=["cart"],
    dependencies=[Depends(auth.get_api_key)],
)

class search_sort_options(str, Enum):
    customer_name = "customer_name"
    item_sku = "item_sku"
    line_item_total = "line_item_total"
    timestamp = "timestamp"

class search_sort_order(str, Enum):
    asc = "asc"
    desc = "desc"   

@router.get("/search/", tags=["search"])
def search_orders(
    customer_name: str = "",
    potion_sku: str = "",
    search_page: str = "",
    sort_col: search_sort_options = search_sort_options.timestamp,
    sort_order: search_sort_order = search_sort_order.desc,
):
    """
    Search for cart line items by customer name and/or potion sku.

    Customer name and potion sku filter to orders that contain the 
    string (case insensitive). If the filters aren't provided, no
    filtering occurs on the respective search term.

    Search page is a cursor for pagination. The response to this
    search endpoint will return previous or next if there is a
    previous or next page of results available. The token passed
    in that search response can be passed in the next search request
    as search page to get that page of results.

    Sort col is which column to sort by and sort order is the direction
    of the search. They default to searching by timestamp of the order
    in descending order.

    The response itself contains a previous and next page token (if
    such pages exist) and the results as an array of line items. Each
    line item contains the line item id (must be unique), item sku, 
    customer name, line item total (in gold), and timestamp of the order.
    Your results must be paginated, the max results you can return at any
    time is 5 total line items.
    """

    return {
        "previous": "",
        "next": "",
        "results": [
            {
                "line_item_id": 1,
                "item_sku": "1 oblivion potion",
                "customer_name": "Scaramouche",
                "line_item_total": 50,
                "timestamp": "2021-01-01T00:00:00Z",
            }
        ],
    }


class Customer(BaseModel):
    customer_name: str
    character_class: str
    level: int

@router.post("/visits/{visit_id}")
def post_visits(visit_id: int, customers: list[Customer]):
    """
    Which customers visited the shop today?
    """
    
    print(customers)
    with db.engine.begin() as connection:
        customers_db = connection.execute(sqlalchemy.text("SELECT customer_name from carts")).fetchall()
        
        customer_names = [customer.customer_name for customer in customers_db]
    print(customer_names)
    return customer_names


@router.post("/")
def create_cart(new_cart: Customer):
    """ """
    with db.engine.begin() as connection:
        cart_id = connection.execute(
            sqlalchemy.text("INSERT INTO carts (customer_name, character_class, level) "
                            "VALUES (:customer_name, :character_class, :level) RETURNING id"),
            {"customer_name": new_cart.customer_name, "character_class": new_cart.character_class, "level": new_cart.level}
        ).scalar_one()
    
        
        # Check if the row is not None and return the ID

        print(f"creating cart for {new_cart.customer_name} with id {cart_id}")

        return {"cart_id": cart_id}


class CartItem(BaseModel):
    quantity: int


@router.post("/{cart_id}/items/{item_sku}")
def set_item_quantity(cart_id: int, item_sku: str, cart_item: CartItem):
    """ """
    with db.engine.begin() as connection:
        item_id = connection.execute(
            sqlalchemy.text("INSERT INTO cart_items (cart_id, item_sku, item_quantity) "
                            "VALUES (:cart_id, :item_sku, :item_quantity) RETURNING item_id"),
            {"cart_id": cart_id, "item_sku": item_sku, "item_quantity": cart_item.quantity}
        ).scalar_one()

    if(item_id):
        return True
    else:
        return False


class CartCheckout(BaseModel):
    payment: str

@router.post("/{cart_id}/checkout")
def checkout(cart_id: int, cart_checkout: CartCheckout):
    """ 
    subtract potions add gold
    """
    # Update global inventory
    with db.engine.begin() as connection:
        
        cart_items = connection.execute(sqlalchemy.text("SELECT * from cart_items")).fetchall()
        total_gold_paid = 0
        total_potions_bought = 0

        for item in cart_items:
            

            # Assuming each item in the cart has a price in gold and quantity
    
            total_potions_bought += item.item_quantity

            # Subtract potions
            connection.execute(
                sqlalchemy.text("UPDATE potions SET quantity = quantity - :quantity WHERE sku = :sku"),
                {"quantity": total_potions_bought, "sku": item.item_sku}
            )
            row = connection.execute(
                sqlalchemy.text("SELECT price from potions WHERE sku = :sku"),
                {"sku": item.item_sku}
            ).fetchone()

            price = row.price
            total_gold_paid += item.item_quantity * price

        
            print(total_potions_bought, total_gold_paid, item.item_sku)

        # Add gold
        connection.execute(
            sqlalchemy.text("UPDATE global_inventory SET gold = gold + :gold"),
            {"gold": total_gold_paid}
        )

    return {"total_potions_bought": total_potions_bought, "total_gold_paid": total_gold_paid}
