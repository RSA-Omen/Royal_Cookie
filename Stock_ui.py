from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QInputDialog, QMessageBox
from ingredient_db import IngredientDB
from stock_logic import StockLogic
from metadata_db import MetadataDB

class IngredientStockPopup(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ingredient Stock Management")
        self.resize(700, 400)

        # --- Data ---
        self.data = []
        self.ingredients_list = []
        self.loading = True  # to ignore initial combo signals

        # --- Buttons ---
        btn_layout = QtWidgets.QHBoxLayout()
        self.add_btn = QtWidgets.QPushButton("Add")
        self.update_btn = QtWidgets.QPushButton("Update")
        self.delete_btn = QtWidgets.QPushButton("Delete")
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.update_btn)
        btn_layout.addWidget(self.delete_btn)

        # --- Input fields ---
        form_layout = QtWidgets.QHBoxLayout()
        self.ingredient_input = QtWidgets.QComboBox()
        self.quantity_input = QtWidgets.QLineEdit()
        self.quantity_input.setPlaceholderText("Quantity")
        form_layout.addWidget(self.ingredient_input)
        form_layout.addWidget(self.quantity_input)

        # --- Table ---
        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Ingredient", "Quantity", "Last Updated"])
        self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

        # --- Layout ---
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addLayout(btn_layout)
        main_layout.addLayout(form_layout)
        main_layout.addWidget(self.table)

        # --- Connect Buttons ---
        self.add_btn.clicked.connect(self.add_stock)
        self.update_btn.clicked.connect(self.update_stock)
        self.delete_btn.clicked.connect(self.delete_stock)
        self.table.cellClicked.connect(self.fill_form)

        # --- Load ingredients ---
        self.load_ingredients()
        self.ingredient_input.currentIndexChanged.connect(self.ingredient_changed)
        self.loading = False

        # --- Initial table load ---
        self.refresh_table()

    def load_ingredients(self):

        self.ingredient_input.blockSignals(True)
        self.ingredient_input.clear()
        self.ingredients_list = IngredientDB.get_ingredients()
        metadata_lookup = {m[0]: m[3] for m in MetadataDB.get_all_metadata()}  # id: unit
        self.ingredient_input.addItem("Other...", -1)
        for ing in self.ingredients_list:
            unit = metadata_lookup.get(ing["MetadataID"], "")
            self.ingredient_input.addItem(f"{ing['Name']} ({ing['Size']} {unit})", ing["ID"])
        self.ingredient_input.setCurrentIndex(0)
        self.ingredient_input.blockSignals(False)

    def ingredient_changed(self, index):
        if self.loading:
            return

        ing_id = self.ingredient_input.itemData(index)
        if ing_id == -1:
            # Add new ingredient
            name, ok = QInputDialog.getText(self, "New Ingredient", "Enter name:")
            if not (ok and name.strip()):
                self.load_ingredients()
                return
            size, ok_size = QInputDialog.getDouble(self, "Size", "Enter size:")
            if not ok_size: return
            unit, ok_unit = QInputDialog.getText(self, "Unit", "Enter unit:")
            if not ok_unit: return
            meta, ok_meta = QInputDialog.getText(self, "Metadata", "Enter metadata:")
            if not ok_meta: return
            IngredientDB.add_ingredient(name.strip(), size, unit.strip(), meta.strip())

            self.loading = True
            self.load_ingredients()
            for i in range(self.ingredient_input.count()):
                if self.ingredient_input.itemText(i).startswith(name.strip()):
                    self.ingredient_input.setCurrentIndex(i)
                    break
            self.loading = False
            return

        # If 'Other...' is selected, show all stock
        if ing_id == -1 or ing_id is None:
            self.refresh_table(ingredient_id=None)
        else:
            self.refresh_table(ingredient_id=ing_id)

    def refresh_table(self, ingredient_id=None):
        try:
            self.data = StockLogic.get_stock(ingredient_id)
            self.table.setRowCount(0)
            for s in self.data:
                row = self.table.rowCount()
                self.table.insertRow(row)
                # s[1] is ingredient_id
                ing = next((i for i in self.ingredients_list if i["ID"] == s[1]), None)
                ing_name = ing["Name"] if ing else f"ID {s[1]}"
                self.table.setItem(row, 0, QtWidgets.QTableWidgetItem(str(s[0])))
                self.table.setItem(row, 1, QtWidgets.QTableWidgetItem(ing_name))
                self.table.setItem(row, 2, QtWidgets.QTableWidgetItem(str(s[3])))
                # s[4] is last_updated if present, else fallback to s[3]
                self.table.setItem(row, 3, QtWidgets.QTableWidgetItem(str(s[4]) if len(s) > 4 else str(s[3])))
        except Exception as e:
            print("Error refreshing stock table:", e)

    def add_stock(self):
        ingredient_id = self.ingredient_input.currentData()
        if ingredient_id is None or ingredient_id == -1:
            QMessageBox.warning(self, "Error", "Select existing ingredient first")
            return
        try:
            quantity = float(self.quantity_input.text().strip())
            StockLogic.add_stock(ingredient_id, quantity)
            self.refresh_table(ingredient_id)
            self.clear_form()
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))

    def update_stock(self):
        selected = self.table.currentRow()
        if selected < 0:
            return
        stock_id = self.data[selected][0]
        try:
            quantity = float(self.quantity_input.text().strip())
            StockLogic.update_stock(stock_id, quantity)
            self.refresh_table(self.ingredient_input.currentData())
            self.clear_form()
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))

    def delete_stock(self):
        selected = self.table.currentRow()
        if selected < 0:
            return
        stock_id = self.data[selected][0]
        try:
            StockLogic.delete_stock(stock_id)
            self.refresh_table(self.ingredient_input.currentData())
            self.clear_form()
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))

    def fill_form(self, row, column):
        s = self.data[row]
        try:
            idx = next(i for i, ing in enumerate(self.ingredients_list) if ing["ID"] == s[1])
            self.ingredient_input.setCurrentIndex(idx + 1)
        except StopIteration:
            self.ingredient_input.setCurrentIndex(0)
        self.quantity_input.setText(str(s[2]))

    def clear_form(self):
        self.quantity_input.clear()
