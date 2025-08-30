from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMessageBox, QTableWidgetItem
from ingredient_db import IngredientDB
from purchases_logic import PurchasesLogic
from metadata_logic import MetadataLogic
from purchases_db import PurchaseDB

class PurchasePopup(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ingredient Purchases")
        self.resize(700, 400)

        self.data = []
        self.ingredients_list = []

        # Buttons
        btn_layout = QtWidgets.QHBoxLayout()
        self.add_btn = QtWidgets.QPushButton("Add")
        self.update_btn = QtWidgets.QPushButton("Update")
        self.delete_btn = QtWidgets.QPushButton("Delete")
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.update_btn)
        btn_layout.addWidget(self.delete_btn)

        # Input fields
        form_layout = QtWidgets.QHBoxLayout()
        self.ingredient_input = QtWidgets.QComboBox()
        self.quantity_input = QtWidgets.QLineEdit(); self.quantity_input.setPlaceholderText("Number of Packages")
        self.price_input = QtWidgets.QLineEdit(); self.price_input.setPlaceholderText("Total Price (all packages)")
        self.discount_input = QtWidgets.QLineEdit(); self.discount_input.setPlaceholderText("Total Discount (all packages)")
        form_layout.addWidget(self.ingredient_input)
        form_layout.addWidget(self.quantity_input)
        form_layout.addWidget(self.price_input)
        form_layout.addWidget(self.discount_input)

        # Table
        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "ID",
            "Ingredient",
            "Date",
            "Packages",
            "Total Price",
            "Total Discount"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

        # Main layout
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addLayout(btn_layout)
        main_layout.addLayout(form_layout)
        main_layout.addWidget(self.table)

        # Connect buttons
        self.add_btn.clicked.connect(self.add_purchase)
        self.update_btn.clicked.connect(self.update_purchase)
        self.delete_btn.clicked.connect(self.delete_purchase)
        self.table.cellClicked.connect(self.fill_form)
        self.ingredient_input.currentIndexChanged.connect(self.on_ingredient_changed)

        # Load ingredients & initial table
        self.load_ingredients()
        self.data = PurchaseDB.get_purchases()
        self.refresh_table()

    def load_ingredients(self):
        self.ingredients_list = IngredientDB.get_ingredients()
        self.metadata_list = MetadataLogic.get_all_metadata()
        self.ingredient_input.clear()
        self.ingredient_input.addItem("Select ingredient...", -1)
        for ing in self.ingredients_list:
            meta = next((m for m in self.metadata_list if m["ID"] == ing["MetadataID"]), None)
            unit = meta["Unit"] if meta else ""
            self.ingredient_input.addItem(f"{ing['Name']} ({ing['Size']} {unit})", ing["ID"])

    def refresh_table(self):
        try:
            self.table.blockSignals(True)
            self.table.setRowCount(0)
            expected_cols = self.table.columnCount()
            for row_index, row_data in enumerate(self.data):
                self.table.insertRow(row_index)
                for col, val in enumerate(row_data):
                    if col >= expected_cols:
                        continue
                    self.table.setItem(row_index, col, QTableWidgetItem(str(val)))
        finally:
            self.table.blockSignals(False)

    def add_purchase(self):
        ingredient_index = self.ingredient_input.currentIndex()
        ingredient_id = self.ingredient_input.itemData(ingredient_index)
        if ingredient_id is None or ingredient_id == -1:
            QMessageBox.warning(self, "Error", "Select an existing ingredient first")
            return

        try:
            quantity = float(self.quantity_input.text() or "0")
            price = float(self.price_input.text() or "0")
            discount = float(self.discount_input.text() or "0")
        except ValueError:
            QMessageBox.warning(self, "Error", "Quantity, Price, Discount must be numbers")
            return
        print("Adding purchase: ", ingredient_id, quantity, price, discount)
        PurchasesLogic.add_purchase(ingredient_id, quantity, price, discount)
        self.on_ingredient_changed(self.ingredient_input.currentIndex())
        self.clear_form()

    def update_purchase(self):
        # You can implement this to call PurchasesLogic.update_purchase(...)
        pass

    def delete_purchase(self):
        # You can implement this to call PurchasesLogic.delete_purchase(...)
        pass

    def fill_form(self, row, column):
        h = self.data[row]
        try:
            idx = next(i for i, ing in enumerate(self.ingredients_list) if ing["ID"] == h[1])
            self.ingredient_input.blockSignals(True)
            self.ingredient_input.setCurrentIndex(idx + 1)
            self.ingredient_input.blockSignals(False)
        except StopIteration:
            self.ingredient_input.blockSignals(True)
            self.ingredient_input.setCurrentIndex(0)
            self.ingredient_input.blockSignals(False)

        self.quantity_input.setText(str(h[3]))
        self.price_input.setText(str(h[4]))
        self.discount_input.setText(str(h[5]))

    def on_ingredient_changed(self, idx):
        pass

    def clear_form(self):
        self.ingredient_input.setCurrentIndex(0)
        self.quantity_input.clear()
        self.price_input.clear()
        self.discount_input.clear()