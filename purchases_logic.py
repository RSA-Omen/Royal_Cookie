from purchases_db import PurchaseDB
from Stock_db import StockDB
from datetime import datetime

class PurchasesLogic:
    @staticmethod
    def add_purchase(ingredient_id, quantity, price, discount):
        purchase_date = datetime.now().isoformat()
        PurchaseDB.add_purchase(ingredient_id, purchase_date, quantity, price, discount)

        # Update stock
        current_stock = StockDB.get_stock(ingredient_id)
        if current_stock:
            stock_id, _, existing_qty, _ = current_stock[0]
            StockDB.update_stock(stock_id, existing_qty + quantity)
        else:
            StockDB.add_stock(ingredient_id, quantity)

    # You can add update_purchase and delete_purchase here as