from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMessageBox, QTableWidgetItem
from ingredient_db import IngredientDB
from purchases_db import PurchaseDB
from datetime import datetime
from Stock_db import IngredientStockDB

class IngredientHistoryPopup(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ingredient Purchase History")
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
        self.quantity_input = QtWidgets.QLineEdit(); self.quantity_input.setPlaceholderText("Quantity")
        self.price_input = QtWidgets.QLineEdit(); self.price_input.setPlaceholderText("Price")
        self.discount_input = QtWidgets.QLineEdit(); self.discount_input.setPlaceholderText("Discount")
        form_layout.addWidget(self.ingredient_input)
        form_layout.addWidget(self.quantity_input)
        form_layout.addWidget(self.price_input)
        form_layout.addWidget(self.discount_input)

        # Table
        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "Ingredient", "Date", "Quantity", "Price", "Discount"])
        self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

        # Main layout
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addLayout(btn_layout)
        main_layout.addLayout(form_layout)
        main_layout.addWidget(self.table)

        # Connect buttons
        self.add_btn.clicked.connect(self.add_history)
        self.update_btn.clicked.connect(self.update_history)
        self.delete_btn.clicked.connect(self.delete_history)
        self.table.cellClicked.connect(self.fill_form)
        self.ingredient_input.currentIndexChanged.connect(self.on_ingredient_changed)

        # Load ingredients & initial table
        self.load_ingredients()
        self.data = PurchaseDB.get_history()
        self.refresh_table()

    def load_ingredients(self):
        self.ingredients_list = IngredientDB.get_ingredients()
        self.ingredient_input.clear()
        self.ingredient_input.addItem("Select ingredient...", -1)
        for ing in self.ingredients_list:
            self.ingredient_input.addItem(f"{ing['Name']} ({ing['Size']} {ing['Unit']})", ing["ID"])

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
                    try:
                        self.table.setItem(row_index, col, QTableWidgetItem(str(val)))
                    except Exception as e:
                        print(f"Failed to set table item at row {row_index}, col {col}: {e}")
        except Exception as e:
            import traceback
            print("Error in refresh_table:", e)
            traceback.print_exc()
        finally:
            self.table.blockSignals(False)

    def add_history(self):
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

        purchase_date = datetime.now().isoformat()
        PurchaseDB.add_history(ingredient_id, purchase_date, quantity, price, discount)

        # --- Add quantity to stock ---
        try:
            current_stock = IngredientStockDB.get_stock(ingredient_id)
            if current_stock:
                # increment existing stock
                stock_id, _, existing_qty, _ = current_stock[0]
                IngredientStockDB.update_stock(stock_id, existing_qty + quantity)
            else:
                # create new stock entry
                IngredientStockDB.add_stock(ingredient_id, quantity)
        except Exception as e:
            print(f"❌ Failed updating stock for ingredient {ingredient_id}: {e}")

        self.on_ingredient_changed(self.ingredient_input.currentIndex())
        self.clear_form()

    def update_history(self):
        selected = self.table.currentRow()
        if selected < 0:
            return

        history_row = self.data[selected]
        history_id = history_row[0]
        ingredient_id = history_row[1]
        old_quantity = float(history_row[3])

        try:
            new_quantity = float(self.quantity_input.text() or "0")
            new_price = float(self.price_input.text() or "0")
            new_discount = float(self.discount_input.text() or "0")
        except ValueError:
            QMessageBox.warning(self, "Error", "Quantity, Price, Discount must be numbers")
            return

        # Update history entry
        PurchaseDB.update_history(history_id, new_quantity, new_price, new_discount)

        # Adjust stock by the difference
        delta = new_quantity - old_quantity
        current_stock_rows = IngredientStockDB.get_stock(ingredient_id)
        if current_stock_rows:
            stock_id, _, stock_quantity, _ = current_stock_rows[0]
            IngredientStockDB.update_stock(stock_id, stock_quantity + delta)
        else:
            # If no stock yet, just add it
            IngredientStockDB.add_stock(ingredient_id, delta)

        # Refresh table and clear form
        self.on_ingredient_changed(self.ingredient_input.currentIndex())
        self.clear_form()

    def delete_history(self):
        selected = self.table.currentRow()
        if selected < 0:
            return

        history_row = self.data[selected]
        history_id = history_row[0]
        ingredient_id = history_row[1]
        old_quantity = float(history_row[3])

        # Delete history entry
        PurchaseDB.delete_history(history_id)

        # Subtract from stock
        current_stock_rows = IngredientStockDB.get_stock(ingredient_id)
        if current_stock_rows:
            stock_id, _, stock_quantity, _ = current_stock_rows[0]
            IngredientStockDB.update_stock(stock_id, stock_quantity - old_quantity)

        # Refresh table and clear form
        self.on_ingredient_changed(self.ingredient_input.currentIndex())
        self.clear_form()

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

    def clear_form(self):
        self.quantity_input.clear()
        self.price_input.clear()
        self.discount_input.clear()

    def on_ingredient_changed(self, index):
        ingredient_id = self.ingredient_input.itemData(index)
        if ingredient_id is not None and ingredient_id != -1:
            self.data = PurchaseDB.get_history(ingredient_id)
        else:
            self.data = PurchaseDB.get_history()
        self.refresh_table()
