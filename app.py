import sys
from PyQt5 import QtWidgets

#we link init all to initialize the database
from init_all import init_db

#load in each UI interface here
from ingredient_ui import IngredientsPopup
from ingredient_history_ui import IngredientHistoryPopup
from ingredient_stock_ui import IngredientStockPopup
from recipes_ui import RecipesPopup
from metadata_ui import MetadataPopup
from customer_ui import CustomerOrdersPopup
from order_ui import OrdersPopup




class MainApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Royal Cookie - Dashboard")
        self.resize(400, 300)

        # --- Buttons on landing page ---
        layout = QtWidgets.QVBoxLayout()
        self.ingredients_btn = QtWidgets.QPushButton("Manage Ingredients")
        self.history_btn = QtWidgets.QPushButton("Ingredient History")
        self.stock_btn = QtWidgets.QPushButton("Manage Stock")
        self.recipes_btn = QtWidgets.QPushButton("Manage Recipes")
        self.metadata_btn = QtWidgets.QPushButton("Manage Metadata")
        self.customers_btn = QtWidgets.QPushButton("Manage Customers")
        self.orders_button = QtWidgets.QPushButton("Manage Orders")

        layout.addWidget(self.ingredients_btn)
        layout.addWidget(self.history_btn)
        layout.addWidget(self.stock_btn)
        layout.addWidget(self.recipes_btn)
        layout.addWidget(self.metadata_btn)
        layout.addWidget(self.customers_btn)
        layout.addWidget(self.orders_button)
        self.setLayout(layout)


        # --- Connect buttons to functions ---
        self.ingredients_btn.clicked.connect(self.open_ingredients)
        self.history_btn.clicked.connect(self.open_history)
        self.stock_btn.clicked.connect(self.open_stock)
        self.recipes_btn.clicked.connect(self.open_recipes)
        self.metadata_btn.clicked.connect(self.open_metadata)
        self.customers_btn.clicked.connect(self.open_customers)
        self.orders_button.clicked.connect(self.open_orders)

    # --- Open windows ---
    def open_ingredients(self):
        self.ingredients_window = IngredientsPopup()
        self.ingredients_window.show()

    def open_history(self):
        self.history_window = IngredientHistoryPopup()
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

    def open_orders(self):
        self.order_window = OrdersPopup()
        self.order_window.show()


if __name__ == "__main__":
    init_db()
    app = QtWidgets.QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec_())
