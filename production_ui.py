from PyQt5 import QtWidgets, QtCore
from production_logic import ProductionController



class ProductionUI(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Production / Order Management")
        self.resize(1200, 800)
        main_layout = QtWidgets.QVBoxLayout(self)

        # Tabs
        self.tabs = QtWidgets.QTabWidget()
        main_layout.addWidget(self.tabs)

        # --- Orders Tab ---
        self.orders_tab = QtWidgets.QWidget()
        orders_layout = QtWidgets.QHBoxLayout(self.orders_tab)

        # Orders Table
        self.orders_table = QtWidgets.QTableWidget()
        self.orders_table.setColumnCount(6)
        self.orders_table.setHorizontalHeaderLabels([
            "Order ID", "Customer", "Status", "Date of delivery", "Total", "Notes"
        ])
        self.orders_table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        orders_layout.addWidget(self.orders_table, 2)
        

        # Order Details Panel
        details_panel = QtWidgets.QTabWidget()
        # Line Items Tab
        self.lineitems_widget = QtWidgets.QWidget()
        lineitems_layout = QtWidgets.QVBoxLayout(self.lineitems_widget)
        self.lineitems_table = QtWidgets.QTableWidget()
        self.lineitems_table.setColumnCount(6)
        self.lineitems_table.setHorizontalHeaderLabels([
            "Line Item", "Recipe", "Qty", "Reserved Qty", "Status", "Notes"
        ])
        self.lineitems_table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        lineitems_layout.addWidget(self.lineitems_table)
        details_panel.addTab(self.lineitems_widget, "Line Items")



        # Ingredients Tab
        self.ingredients_widget = QtWidgets.QWidget()
        ingredients_layout = QtWidgets.QVBoxLayout(self.ingredients_widget)
        self.ingredients_table = QtWidgets.QTableWidget()
        self.ingredients_table.setColumnCount(6)
        self.ingredients_table.setHorizontalHeaderLabels([
            "Ingredient", "Required", "Reserved", "Available", "Shortage", "Batch/Expiry"
        ])
        self.ingredients_table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        ingredients_layout.addWidget(self.ingredients_table)
        details_panel.addTab(self.ingredients_widget, "Required Ingredients")

        # Production Notes Tab
        self.notes_widget = QtWidgets.QWidget()
        notes_layout = QtWidgets.QVBoxLayout(self.notes_widget)
        self.notes_text = QtWidgets.QTextEdit()
        notes_layout.addWidget(self.notes_text)
        details_panel.addTab(self.notes_widget, "Production Notes")

        orders_layout.addWidget(details_panel, 3)
        self.tabs.addTab(self.orders_tab, "Orders")

        # --- Reservations Tab ---
        self.reservations_tab = QtWidgets.QWidget()
        reservations_layout = QtWidgets.QVBoxLayout(self.reservations_tab)
        self.reservations_table = QtWidgets.QTableWidget()
        self.reservations_table.setColumnCount(9)
        self.reservations_table.setHorizontalHeaderLabels([
            "Reservation ID", "Order", "Line Item", "Ingredient", "Batch", "Purchase Date",
            "Expiry", "Qty", "Reserved Until"
        ])
        self.reservations_table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        # Ensure row selection and multi-select is enabled
        self.reservations_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.reservations_table.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        reservations_layout.addWidget(self.reservations_table)
        self.tabs.addTab(self.reservations_tab, "Reservations")

        # --- Inventory Tab ---
        self.inventory_tab = QtWidgets.QWidget()
        inventory_layout = QtWidgets.QVBoxLayout(self.inventory_tab)
        self.inventory_table = QtWidgets.QTableWidget()
        self.inventory_table.setColumnCount(6)
        self.inventory_table.setHorizontalHeaderLabels([
            "Ingredient", "Batch", "Purchase Date", "Expiry", "Qty Available", "Qty Reserved"
        ])
        self.inventory_table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        inventory_layout.addWidget(self.inventory_table)
        self.tabs.addTab(self.inventory_tab, "Inventory")

        # --- Shopping List Tab ---
        self.shopping_tab = QtWidgets.QWidget()
        shopping_layout = QtWidgets.QVBoxLayout(self.shopping_tab)
        self.shopping_table = QtWidgets.QTableWidget()
        self.shopping_table.setColumnCount(4)
        self.shopping_table.setHorizontalHeaderLabels([
            "Ingredient", "Qty Needed", "Orders Needing", "Mark as Purchased"
        ])
        self.shopping_table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        shopping_layout.addWidget(self.shopping_table)
        self.tabs.addTab(self.shopping_tab, "Shopping List")

        # --- Action Buttons (bottom) ---
        btn_layout = QtWidgets.QHBoxLayout()
        self.reserve_btn = QtWidgets.QPushButton("Reserve Ingredients")
        self.release_btn = QtWidgets.QPushButton("Release Reservation")
        self.status_btn = QtWidgets.QPushButton("Change Order Status")
        self.add_note_btn = QtWidgets.QPushButton("Add Production Note")
        btn_layout.addWidget(self.reserve_btn)
        btn_layout.addWidget(self.release_btn)
        btn_layout.addWidget(self.status_btn)
        btn_layout.addWidget(self.add_note_btn)
        main_layout.addLayout(btn_layout)

        self.controller = ProductionController(self)

if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    window = ProductionUI()
    window.show()
    app.exec_()