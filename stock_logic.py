from Stock_db import StockDB

class StockLogic:
    @staticmethod
    def get_stock(ingredient_id=None):
        return StockDB.get_stock(ingredient_id)

    @staticmethod
    def add_stock(ingredient_id, quantity):
        if not isinstance(quantity, (int, float)) or quantity <= 0:
            raise ValueError("Quantity must be a positive number.")
        return StockDB.add_stock(ingredient_id, quantity)

    @staticmethod
    def update_stock(stock_id, quantity):
        if not isinstance(quantity, (int, float)) or quantity <= 0:
            raise ValueError("Quantity must be a positive number.")
        return StockDB.update_stock(stock_id, quantity)

    @staticmethod
    def delete_stock(stock_id):
        return StockDB.delete_stock(stock_id)
