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
    """
    General Idea:
    prev initially "" but on click next, there will be prev button. strings det. whether dsiplay button.
    """
    
    metadata = sqlalchemy.MetaData()

    cart_items = sqlalchemy.Table(
        'cart_items',
        metadata,
        sqlalchemy.Column('item_id', sqlalchemy.Integer, primary_key=True),
        sqlalchemy.Column('item_sku', sqlalchemy.String),
        sqlalchemy.Column('item_quantity', sqlalchemy.Integer),
        sqlalchemy.Column('timestamp', sqlalchemy.DateTime),
        sqlalchemy.Column('cart_id', sqlalchemy.Integer),
        sqlalchemy.Column('potion_id', sqlalchemy.Integer)
    )

    carts = sqlalchemy.Table(
        'carts',
        metadata,
        sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True),
        sqlalchemy.Column('customer_name', sqlalchemy.String),
        sqlalchemy.Column('timestamp', sqlalchemy.DateTime),
        sqlalchemy.Column('character_class', sqlalchemy.String),
        sqlalchemy.Column('level', sqlalchemy.Integer),
    )

    potions = sqlalchemy.Table(
        'potions',
        metadata,
        sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True),
        sqlalchemy.Column('price', sqlalchemy.Float),
    
    )

    if sort_col == search_sort_options.timestamp:
        order_by = cart_items.c.timestamp
    elif sort_col == search_sort_options.customer_name:
        order_by = carts.c.customer_name
    elif sort_col == search_sort_options.item_sku:
        order_by = cart_items.c.item_sku
    elif sort_col == search_sort_options.line_item_total:
        order_by = cart_items.c.line_item_total
    else:
        raise ValueError("Invalid sort column")

    if sort_col != search_sort_options.timestamp and sort_order == search_sort_order.desc:
        order_by = sqlalchemy.desc(order_by)

    stmt = (
        sqlalchemy.select(
            cart_items.c.item_id,
            cart_items.c.item_sku,
            carts.c.customer_name,
            (cart_items.c.item_quantity * potions.c.price).label("line_item_total"),
            cart_items.c.timestamp
        )
        .select_from(
            cart_items
            .join(carts, cart_items.c.cart_id == carts.c.id)
            .join(potions, cart_items.c.potion_id == potions.c.id)
        )
        .limit(5)
        .order_by(order_by, cart_items.c.item_id)
    )

    if customer_name:
        stmt = stmt.where(carts.c.customer_name.ilike(f"%{customer_name}%"))
    if potion_sku:
        # Adjust the condition to filter by item_sku in cart_items
        stmt = stmt.where(cart_items.c.item_sku.ilike(f"%{potion_sku}%"))

    prev_token = ""
    next_token = ""
    if search_page:
        if sort_order == search_sort_order.desc:
            stmt = stmt.where(cart_items.c.timestamp < search_page)
        else:
            stmt = stmt.where(cart_items.c.timestamp > search_page)
    
    with db.engine.begin() as connection:
        result = connection.execute(stmt)
        json_result = []
        for row in result:
            json_result.append({
                "line_item_id": row.item_id,
                "item_sku": row.item_sku,
                "customer_name": row.customer_name,
                "line_item_total": row.line_item_total,
                "timestamp": row.timestamp.strftime("%Y-%m-%dT%H:%M:%SZ")  # ISO 8601
            })

        # checking if there are previous or next pages
        # You need to adjust this logic based on the actual database structure
        # and the way you're handling pagination
        if search_page:
            # Check if there are more previous results
            prev_stmt = stmt.offset(-5)
            prev_result = connection.execute(prev_stmt)
            if prev_result.fetchall():
                prev_token = "previous"
            
            # Check if there are more next results
            next_stmt = stmt.offset(5)
            next_result = connection.execute(next_stmt)
            if next_result.fetchall():
                next_token = "next"

    # Return the results along with previous and next tokens
    return {
        "previous": prev_token,
        "next": next_token,
        "results": json_result
    }

    # return {
    #     "previous": "",
    #     "next": "",
    #     "results": [
    #         {
    #             "line_item_id": 1,
    #             "item_sku": "1 oblivion potion",
    #             "customer_name": "Scaramouche",
    #             "line_item_total": 50,
    #             "timestamp": "2021-01-01T00:00:00Z",
    #         }
    #     ],
    # }


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
        potion_id = connection.execute(
            sqlalchemy.text("SELECT id AS potion_id FROM potions WHERE sku = :sku"),
            {"sku": item_sku }
        ).scalar()

        print("POTID", potion_id)

        item_id = connection.execute(
            sqlalchemy.text("INSERT INTO cart_items (potion_id, cart_id, item_sku, item_quantity) "
                            "VALUES (:potion_id, :cart_id, :item_sku, :item_quantity) RETURNING item_id"),
            {"potion_id": potion_id, "cart_id": cart_id, "item_sku": item_sku, "item_quantity": cart_item.quantity}
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
        
        cart_items = connection.execute(sqlalchemy.text("SELECT * from cart_items WHERE cart_id = :cart_id"),
            {"cart_id": cart_id}).fetchall()
        total_gold_paid = 0
        total_potions_bought = 0

        for item in cart_items:
            
            # Assuming each item in the cart has a price in gold and quantity
    
            total_potions_bought += item.item_quantity

            ###LEDGER
            connection.execute(sqlalchemy.text("INSERT INTO potion_ledgers (potion_id, change) VALUES (:potion_id, :change)"),
                    {"potion_id": item.potion_id, "change": -(total_potions_bought)}
                    )

            row = connection.execute(
                sqlalchemy.text("SELECT price from potions WHERE sku = :sku"),
                {"sku": item.item_sku}
            ).fetchone()

            price = row.price
            total_gold_paid += item.item_quantity * price

            print(total_potions_bought, total_gold_paid, item.item_sku)

        
        ##LEDGER
        connection.execute(
                    sqlalchemy.text("INSERT INTO gold_ledgers (change) VALUES (:change)"),
                    {"change": total_gold_paid})
                

    return {"total_potions_bought": total_potions_bought, "total_gold_paid": total_gold_paid}
