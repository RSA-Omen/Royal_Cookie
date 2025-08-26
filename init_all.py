import sqlite3
import db as DB_handler
import line_item_db
#imports each class for the purpose of accessing the initializers.
from ingredient_db import IngredientDB
from ingredient_stock_db import IngredientStockDB
from recipe_db import RecipeDB
from ingredient_history_db import IngredientHistoryDB
from metadata_db import MetadataDB
from customer_db import CustomerDB
from order_db import OrderDB
from line_item_db import LineItemDB
# the main database initializer


def init_db():
    """Initialize all tables in the database."""
    connection = DB_handler.get_connection()
    IngredientDB.init_ingredient_db(connection)
    IngredientStockDB.init_ingredient_stock_db(connection)
    RecipeDB.init_recipe_db(connection)
    MetadataDB.init_metadata_db(connection)
    IngredientHistoryDB.init_ingredient_history_db(connection)
    CustomerDB.init_customer_db(connection)
    OrderDB.init_orders_table(connection)
    LineItemDB.init_line_items_table(connection)
    connection.close()