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
            row = current_stock[0]
            stock_id = row[0]         # id
            existing_qty = row[3]     # quantity
            StockDB.update_stock(stock_id, existing_qty + quantity)
        else:
            StockDB.add_stock(ingredient_id, quantity)

    @staticmethod
    def get_purchases(ingredient_id=None):
        return PurchaseDB.get_purchases(ingredient_id)


    @staticmethod
    def update_purchase(purchase_id, quantity, price, discount):
        PurchaseDB.update_purchase(purchase_id, quantity, price, discount)

    @staticmethod
    def delete_purchase(purchase_id):
        PurchaseDB.delete_purchase(purchase_id)