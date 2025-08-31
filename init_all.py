import sqlite3
import db as DB_handler
import line_item_db
#imports each class for the purpose of accessing the initializers.
from ingredient_db import IngredientDB
from Stock_db import StockDB
from recipe_db import RecipeDB
from purchases_db import PurchaseDB
from metadata_db import MetadataDB
from customer_db import CustomerDB
from order_db import OrderDB
from line_item_db import LineItemDB
from reservation_db import ReservationDB
from recipe_ingredients import RecipeIngredientDB
# the main database initializer


def init_db():
    """Initialize all tables in the database."""
    connection = DB_handler.get_connection()

    IngredientDB.init_ingredient_db(connection)
    StockDB.init_stock_db(connection)
    RecipeDB.init_recipe_db(connection)
    MetadataDB.init_metadata_db(connection)
    PurchaseDB.init_ingredient_purchases_db(connection)
    CustomerDB.init_customer_db(connection)
    OrderDB.init_orders_table(connection)
    ReservationDB.init_reservations_db(connection)
    LineItemDB.init_line_items_table(connection)
    RecipeIngredientDB.init_recipe_ingredients_db(connection)

    connection.close()