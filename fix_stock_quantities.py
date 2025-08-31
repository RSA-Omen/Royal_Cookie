# Script to fix stock quantities in the database
# For each stock entry, set quantity = number_of_units_purchased * ingredient_size
# This assumes that the original number of units purchased is stored in the purchases table

from Stock_db import StockDB
from ingredient_db import IngredientDB
from purchases_db import PurchaseDB
from db import get_connection

# Get all stock entries
stock_rows = StockDB.get_stock()

conn = get_connection()
cursor = conn.cursor()

for stock in stock_rows:
    stock_id = stock[0]
    ingredient_id = stock[1]
    # Find the most recent purchase for this ingredient (assume 1:1 for simplicity)
    cursor.execute("SELECT quantity FROM ingredient_purchases WHERE ingredient_id = ? ORDER BY id DESC LIMIT 1", (ingredient_id,))
    purchase_row = cursor.fetchone()
    if not purchase_row:
        print(f"No purchase found for ingredient_id {ingredient_id}, skipping.")
        continue
    units_purchased = purchase_row[0]
    ingredient = IngredientDB.get_ingredient_by_id(ingredient_id)
    if not ingredient or "Size" not in ingredient:
        print(f"No size found for ingredient_id {ingredient_id}, skipping.")
        continue
    size = ingredient["Size"]
    correct_qty = units_purchased * size
    # Update stock quantity
    cursor.execute("UPDATE stock SET quantity = ? WHERE id = ?", (correct_qty, stock_id))
    print(f"Updated stock_id {stock_id}: {units_purchased} x {size}g = {correct_qty}g")

conn.commit()
conn.close()
print("Stock quantities updated.")
