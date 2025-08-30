import sys
from PyQt5 import QtWidgets

from init_all import init_db
from ingredient_ui import IngredientsPopup
from purchases_ui import PurchasePopup
from Stock_ui import IngredientStockPopup
from recipes_ui import RecipesPopup
from metadata_ui import MetadataPopup
from customer_ui import CustomerOrdersPopup
from order_ui import OrdersPopup
from production_ui import ProductionUI

class MainApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Royal Cookie - Dashboard")
        self.resize(600, 400)

        # Central widget
        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        layout = QtWidgets.QVBoxLayout()
        central.setLayout(layout)
        layout.addWidget(QtWidgets.QLabel("Select an option from the menu above"))



        # --- Menu Bar ---
        menubar = self.menuBar()

        # Ingredients menu
        ingredients_menu = menubar.addMenu("Ingredients")
        ingredients_menu.addAction("Manage Ingredients", self.open_ingredients)
        ingredients_menu.addAction("Ingredient Purchase", self.open_history)
        ingredients_menu.addAction("Manage Stock", self.open_stock)

        # Recipes menu
        recipes_menu = menubar.addMenu("Recipes")
        recipes_menu.addAction("Manage Recipes", self.open_recipes)
        recipes_menu.addAction("Manage Metadata", self.open_metadata)

        # Customers / Orders menu
        customers_menu = menubar.addMenu("Customers & Orders")
        customers_menu.addAction("Manage Customers", self.open_customers)
        customers_menu.addAction("Production Dashboard", self.open_dashboard)

    # --- Open windows ---
    def open_ingredients(self):
        self.ingredients_window = IngredientsPopup()
        self.ingredients_window.show()

    def open_history(self):
        self.history_window = PurchasePopup()
        self.history_window.show()

    def open_stock(self):
        self.stock_window = IngredientStockPopup()
        self.stock_window.show()

    def open_recipes(self):
        self.recipes_window = RecipesPopup()
        self.recipes_window.show()

    def open_metadata(self):
        self.metadata_window = MetadataPopup()
        self.metadata_window.show()

    def open_customers(self):
        self.customers_window = CustomerOrdersPopup()
        self.customers_window.show()

    def open_dashboard(self):
        self.production_window = ProductionUI()
        self.production_window.show()


if __name__ == "__main__":
    init_db()
    app = QtWidgets.QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec_())
