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
        orders_layout = QtWidgets.QVBoxLayout(self.orders_tab)

        # Order selection combobox with toggle
        order_select_layout = QtWidgets.QHBoxLayout()
        order_select_layout.addWidget(QtWidgets.QLabel("Select Order:"))
        self.order_combo = QtWidgets.QComboBox()
        order_select_layout.addWidget(self.order_combo)
        self.show_closed_toggle = QtWidgets.QPushButton("Show Closed Orders")
        self.show_closed_toggle.setCheckable(True)
        self.show_closed_toggle.setChecked(False)
        order_select_layout.addWidget(self.show_closed_toggle)
        orders_layout.addLayout(order_select_layout)

        # Order details fields
        details_form = QtWidgets.QFormLayout()
        self.order_id_field = QtWidgets.QLineEdit(); self.order_id_field.setReadOnly(True)
        self.customer_field = QtWidgets.QLineEdit(); self.customer_field.setReadOnly(True)
        self.status_field = QtWidgets.QLineEdit(); self.status_field.setReadOnly(True)
        self.delivery_date_field = QtWidgets.QLineEdit(); self.delivery_date_field.setReadOnly(True)
        self.total_field = QtWidgets.QLineEdit(); self.total_field.setReadOnly(True)
        self.notes_field = QtWidgets.QLineEdit(); self.notes_field.setReadOnly(True)
        details_form.addRow("Order ID:", self.order_id_field)
        details_form.addRow("Customer:", self.customer_field)
        details_form.addRow("Status:", self.status_field)
        details_form.addRow("Date of delivery:", self.delivery_date_field)
        details_form.addRow("Total:", self.total_field)
        details_form.addRow("Notes:", self.notes_field)
        orders_layout.addLayout(details_form)

        # Order Details Panel (tabs)
        details_panel = QtWidgets.QTabWidget()
        # Line Items Tab
        self.lineitems_widget = QtWidgets.QWidget()
        lineitems_layout = QtWidgets.QVBoxLayout(self.lineitems_widget)
        self.lineitems_table = QtWidgets.QTableWidget()
        self.lineitems_table.setColumnCount(5)
        self.lineitems_table.setHorizontalHeaderLabels([
            "Recipe", "Qty", "Reserved Qty", "Status", "Notes"
        ])
        self.lineitems_table.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        self.lineitems_table.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        self.lineitems_table.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        self.lineitems_table.horizontalHeader().setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)
        self.lineitems_table.horizontalHeader().setSectionResizeMode(4, QtWidgets.QHeaderView.Stretch)
        self.lineitems_table.setColumnWidth(4, self.lineitems_table.columnWidth(4) * 3)
        lineitems_layout.addWidget(self.lineitems_table)

        # Ingredients for selected line item table
        self.ingredients_for_lineitem_table = QtWidgets.QTableWidget()
        self.ingredients_for_lineitem_table.setColumnCount(4)
        self.ingredients_for_lineitem_table.setHorizontalHeaderLabels([
            "Ingredient", "Quantity", "Available", "Reserved"
        ])
        self.ingredients_for_lineitem_table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        lineitems_layout.addWidget(QtWidgets.QLabel("Ingredients Summary for Order:"))
        lineitems_layout.addWidget(self.ingredients_for_lineitem_table)

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

        orders_layout.addWidget(details_panel)
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
    # Ensure the order combo is populated after all UI setup
        self.controller.populate_order_combo()

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = ProductionUI()
    window.show()
    sys.exit(app.exec_())