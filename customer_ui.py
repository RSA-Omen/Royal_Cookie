from PyQt5 import QtWidgets, QtCore ,QtGui
from PyQt5.QtWidgets import QInputDialog, QMessageBox
from customer_db import CustomerDB
from order_db import OrderDB
from line_item_db import LineItemDB
from metadata_db import MetadataDB
from Stock_db import IngredientStockDB
from recipe_db import RecipeDB


class StockCheckPanel(QtWidgets.QWidget):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QtWidgets.QVBoxLayout(self)

        # Summary Table
        self.summary_table = QtWidgets.QTableWidget()
        self.summary_table.setColumnCount(4)
        self.summary_table.setHorizontalHeaderLabels(["Ingredient", "Required", "Available", "Status"])
        self.summary_table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        layout.addWidget(QtWidgets.QLabel("Summary Table"))
        layout.addWidget(self.summary_table)

        # Breakdown Tree
        self.breakdown_tree = QtWidgets.QTreeWidget()
        self.breakdown_tree.setHeaderLabels(["Recipe/Ingredient", "Required", "Available", "Status"])
        layout.addWidget(QtWidgets.QLabel("Breakdown Tree"))
        layout.addWidget(self.breakdown_tree)    

    def load_stock(self, order_id):
        items = LineItemDB.get_order_items(order_id) or []
        if not items:
            print(f"[DEBUG] No line items found for order {order_id}")
            self.summary_table.setRowCount(0)
            self.breakdown_tree.clear()
            return

        stock_db = IngredientStockDB()
        ingredient_totals = {}
        self.breakdown_tree.clear()

        for item in items:
            lineitem_id, order_id, recipe_name, qty = item
            recipe_name = str(recipe_name or "Unnamed Recipe")
            qty = qty or 0

            recipe_node = QtWidgets.QTreeWidgetItem([recipe_name])
            self.breakdown_tree.addTopLevelItem(recipe_node)

            recipe_id = LineItemDB.get_recipe_id(lineitem_id)
            if not recipe_id:
                continue

            ingredients = RecipeDB.get_recipe_ingredients(recipe_id) or []
            for ri_id, r_id, metadata_id, per_recipe_amt, unit, ing_name in ingredients:
                ing_name = str(ing_name or "Unnamed Ingredient")
                per_recipe_amt = per_recipe_amt or 0
                required = per_recipe_amt * qty
                available = stock_db.get_available_stock(metadata_id) or 0

                # For summary table
                if metadata_id not in ingredient_totals:
                    ingredient_totals[metadata_id] = {"name": ing_name, "required": 0, "available": available}
                ingredient_totals[metadata_id]["required"] += required

                status = self._status(required, available)
                ing_item = QtWidgets.QTreeWidgetItem([ing_name, str(required), str(available), status])
                self._color_row(ing_item, status)
                recipe_node.addChild(ing_item)
          
            # --- Populate the summary table ---
        self.summary_table.setRowCount(len(ingredient_totals))
        for row, ing in enumerate(ingredient_totals.values()):
            name = str(ing.get("name", ""))
            required = ing.get("required", 0)
            available = ing.get("available", 0)
            status = self._status(required, available)

            self.summary_table.setItem(row, 0, QtWidgets.QTableWidgetItem(name))
            self.summary_table.setItem(row, 1, QtWidgets.QTableWidgetItem(str(required)))
            self.summary_table.setItem(row, 2, QtWidgets.QTableWidgetItem(str(available)))
            self.summary_table.setItem(row, 3, QtWidgets.QTableWidgetItem(status))

            self._color_row_table(row, status)

    def _status(self, required, available):
        if available >= required:
            return "✅ Enough"
        elif available > 0:
            return "⚠️ Low"
        else:
            return "❌ Missing"
    def _color_row(self, item, status):
        if "Enough" in status:
            color = QtGui.QColor(144, 238, 144)  # light green
        elif "Low" in status:
            color = QtGui.QColor(255, 165, 0)    # orange
        else:
            color = QtGui.QColor(255, 99, 71)    # red
        for col in range(item.columnCount()):
            item.setBackground(col, color)
    def _color_row_table(self, row, status):
        if "Enough" in status:
            color = QtGui.QColor(144, 238, 144)
        elif "Low" in status:
            color = QtGui.QColor(255, 165, 0)
        else:
            color = QtGui.QColor(255, 99, 71)
        for col in range(self.summary_table.columnCount()):
            self.summary_table.item(row, col).setBackground(color)

class AddCustomerDialog(QtWidgets.QDialog):
    """Popup dialog for adding a new customer"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add New Customer")
        self.setModal(True)
        self.resize(400, 250)

        # --- Form layout ---
        form_layout = QtWidgets.QFormLayout()
        self.name_input = QtWidgets.QLineEdit()
        self.phone_input = QtWidgets.QLineEdit()
        self.email_input = QtWidgets.QLineEdit()
        self.subscribed_checkbox = QtWidgets.QCheckBox("Subscribed")
        self.address_input = QtWidgets.QLineEdit()
        self.notes_input = QtWidgets.QLineEdit()

        form_layout.addRow("Name:", self.name_input)
        form_layout.addRow("Phone:", self.phone_input)
        form_layout.addRow("Email:", self.email_input)
        form_layout.addRow("", self.subscribed_checkbox)
        form_layout.addRow("Address:", self.address_input)
        form_layout.addRow("Notes:", self.notes_input)

        # --- Buttons ---
        btn_layout = QtWidgets.QHBoxLayout()
        self.add_btn = QtWidgets.QPushButton("Add")
        self.cancel_btn = QtWidgets.QPushButton("Cancel")
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.cancel_btn)

        # --- Main layout ---
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addLayout(form_layout)
        main_layout.addLayout(btn_layout)

        # --- Events ---
        self.add_btn.clicked.connect(self.add_customer)
        self.cancel_btn.clicked.connect(self.reject)

    def add_customer(self):
        """Insert customer into DB"""
        name = self.name_input.text().strip()
        phone = self.phone_input.text().strip()
        email = self.email_input.text().strip()
        subscribed = 1 if self.subscribed_checkbox.isChecked() else 0
        address = self.address_input.text().strip()
        notes = self.notes_input.text().strip()

        if not name or not phone:
            QtWidgets.QMessageBox.warning(self, "Validation Error", "Name and Phone are required.")
            return

        CustomerDB.add_customer(name, phone, email, subscribed, address, notes)
        self.accept()

class CustomerOrdersPopup(QtWidgets.QWidget):
    """Main window containing customers, orders, and line items"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Customer Orders Manager")
        self.resize(1200, 700)

        main_layout = QtWidgets.QHBoxLayout(self)

        # LEFT PANEL
        left_layout = QtWidgets.QVBoxLayout()
        left_layout.addWidget(QtWidgets.QLabel("Customers"))
        self.customer_list = QtWidgets.QListWidget()
        self.customer_list.currentItemChanged.connect(self.on_customer_selected)
        left_layout.addWidget(self.customer_list)
        self.delete_btn = QtWidgets.QPushButton("Delete Customer")
        self.add_customer_btn = QtWidgets.QPushButton("Add Customer")
        left_layout.addWidget(self.delete_btn)
        left_layout.addWidget(self.add_customer_btn)
        self.delete_btn.clicked.connect(self.delete_selected_customer)
        self.add_customer_btn.clicked.connect(self.show_add_customer_dialog)

             # MIDDLE PANEL
        middle_layout = QtWidgets.QVBoxLayout()
        self.profile_group = QtWidgets.QGroupBox("Customer Profile")
        profile_layout = QtWidgets.QFormLayout()
        self.name_input = QtWidgets.QLineEdit(); self.name_input.setPlaceholderText("Name")
        self.phone_input = QtWidgets.QLineEdit(); self.phone_input.setPlaceholderText("Phone")
        self.email_input = QtWidgets.QLineEdit(); self.email_input.setPlaceholderText("Email")
        self.subscribed_checkbox = QtWidgets.QCheckBox("Subscribed")
        self.address_input = QtWidgets.QLineEdit(); self.address_input.setPlaceholderText("Address")
        self.notes_input = QtWidgets.QLineEdit(); self.notes_input.setPlaceholderText("Notes")
        profile_layout.addRow("Name:", self.name_input)
        profile_layout.addRow("Phone:", self.phone_input)
        profile_layout.addRow("Email:", self.email_input)
        profile_layout.addRow("", self.subscribed_checkbox)
        profile_layout.addRow("Address:", self.address_input)
        profile_layout.addRow("Notes:", self.notes_input)
        self.profile_group.setLayout(profile_layout)
        middle_layout.addWidget(self.profile_group, 1)

        self.name_input.textChanged.connect(lambda: self.update_customer_field('name'))
        self.phone_input.textChanged.connect(lambda: self.update_customer_field('phone'))
        self.email_input.textChanged.connect(lambda: self.update_customer_field('email'))
        self.subscribed_checkbox.stateChanged.connect(lambda _: self.update_customer_field('subscribed'))
        self.address_input.textChanged.connect(lambda: self.update_customer_field('address'))
        self.notes_input.textChanged.connect(lambda: self.update_customer_field('notes'))

        self.orders_group = QtWidgets.QGroupBox("Orders")
        orders_layout = QtWidgets.QVBoxLayout()
        self.order_table = QtWidgets.QTableWidget()
        self.order_table.setColumnCount(3)
        self.order_table.setHorizontalHeaderLabels(["Order ID", "Date", "Status"])
        self.order_table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        orders_layout.addWidget(self.order_table)
        self.add_order_btn = QtWidgets.QPushButton("Add Order")
        self.edit_order_btn = QtWidgets.QPushButton("Edit Order")
        self.delete_order_btn = QtWidgets.QPushButton("Delete Order")
        orders_layout.addWidget(self.add_order_btn)
        orders_layout.addWidget(self.edit_order_btn)
        orders_layout.addWidget(self.delete_order_btn)
        self.orders_group.setLayout(orders_layout)
        middle_layout.addWidget(self.orders_group, 2)
        self.add_order_btn.clicked.connect(self.add_order)
        self.edit_order_btn.clicked.connect(self.update_order)
        self.delete_order_btn.clicked.connect(self.delete_order)
        self.order_table.currentCellChanged.connect(self.on_order_selected)

        # RIGHT PANEL
        right_layout = QtWidgets.QVBoxLayout()
        right_layout.addWidget(QtWidgets.QLabel("Line Items"))
        self.lineitem_table = QtWidgets.QTableWidget()
        self.lineitem_table.setColumnCount(3)
        self.lineitem_table.setHorizontalHeaderLabels(["Line Item ID", "Product/Recipe", "Qty"])
        self.lineitem_table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        right_layout.addWidget(self.lineitem_table)
        self.add_lineitem_btn = QtWidgets.QPushButton("Add Line Item")
        self.edit_lineitem_btn = QtWidgets.QPushButton("Edit Line Item")
        self.delete_lineitem_btn = QtWidgets.QPushButton("Delete Line Item")
        right_layout.addWidget(self.add_lineitem_btn)
        right_layout.addWidget(self.edit_lineitem_btn)
        right_layout.addWidget(self.delete_lineitem_btn)
        self.add_lineitem_btn.setEnabled(False)
        self.edit_lineitem_btn.setEnabled(False)
        self.delete_lineitem_btn.setEnabled(False)
        self.add_lineitem_btn.clicked.connect(self.add_line_item)
        self.edit_lineitem_btn.clicked.connect(self.update_line_item)
        self.delete_lineitem_btn.clicked.connect(self.delete_line_item)

        # Stock Check Panel (C3R2)
        right_layout.addWidget(QtWidgets.QLabel("Stock Check (C3R2)"))
        self.stock_check_panel = StockCheckPanel()
        right_layout.addWidget(self.stock_check_panel)
        main_layout.addLayout(left_layout, 1)
        main_layout.addLayout(middle_layout, 2)
        main_layout.addLayout(right_layout, 2)
        self.refresh_customers()

    # ---------------- LEFT PANEL FUNCS ----------------
    def refresh_customers(self):
        self.customer_list.clear()
        self.customers = CustomerDB.get_customers()
        for c in self.customers:
            item = QtWidgets.QListWidgetItem(f"{c[1]} ({c[2]})")
            item.setData(QtCore.Qt.UserRole, c[0])
            self.customer_list.addItem(item)
    def show_add_customer_dialog(self):
        dialog = AddCustomerDialog(self)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            self.refresh_customers()
            # Auto-select the newly added customer
            new_customer = CustomerDB.get_customers()[-1]  # assumes last added
            for i in range(self.customer_list.count()):
                item = self.customer_list.item(i)
                if item.data(QtCore.Qt.UserRole) == new_customer[0]:
                    self.customer_list.setCurrentItem(item)
                    break
    def delete_selected_customer(self):
        if not hasattr(self, "selected_id"):
            QtWidgets.QMessageBox.warning(self, "Delete Error", "No customer selected.")
            return
        reply = QtWidgets.QMessageBox.question(
            self, "Confirm Delete", "Are you sure you want to delete this customer?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
        if reply == QtWidgets.QMessageBox.Yes:
            CustomerDB.delete_customer(self.selected_id)
            self.selected_id = None
            self.name_input.clear(); self.phone_input.clear(); self.email_input.clear()
            self.subscribed_checkbox.setChecked(False)
            self.address_input.clear(); self.notes_input.clear()
            self.order_table.setRowCount(0); self.lineitem_table.setRowCount(0)
            self.refresh_customers()
    # ---------------- MIDDLE PANEL FUNCS ----------------
    def on_customer_selected(self, current, previous):
        if not current: return
        cid = current.data(QtCore.Qt.UserRole)
        customer = next((c for c in self.customers if c[0] == cid), None)
        if not customer: return

        self.updating_fields = True
        self.selected_id = cid
        self.selected_customer_id = cid
        self.name_input.setText(customer[1])
        self.phone_input.setText(customer[2])
        self.email_input.setText(customer[3])
        self.subscribed_checkbox.setChecked(customer[4] == 1)
        self.address_input.setText(customer[5])
        self.notes_input.setText(customer[6])
        self.updating_fields = False

        self.lineitem_table.setRowCount(0)
        self.load_orders()
    def update_customer_field(self, field):
        if not hasattr(self, "selected_id") or getattr(self, "updating_fields", False):
            return
        cid = self.selected_id
        value_map = {
            'name': self.name_input.text(),
            'phone': self.phone_input.text(),
            'email': self.email_input.text(),
            'subscribed': 1 if self.subscribed_checkbox.isChecked() else 0,
            'address': self.address_input.text(),
            'notes': self.notes_input.text()
        }
        CustomerDB.update_customer(cid, **{field: value_map[field]})
        self.refresh_customers()
    def load_orders(self):
        if not hasattr(self, "selected_customer_id"):
            return
        self.order_table.setRowCount(0)
        orders = OrderDB.get_orders_by_customer(self.selected_customer_id)
        for order in orders:
            row = self.order_table.rowCount()
            self.order_table.insertRow(row)
            self.order_table.setItem(row, 0, QtWidgets.QTableWidgetItem(str(order[0])))
            self.order_table.setItem(row, 1, QtWidgets.QTableWidgetItem(order[1]))
            self.order_table.setItem(row, 2, QtWidgets.QTableWidgetItem(order[2]))

    def add_order(self):
        try:
            if not hasattr(self, "selected_customer_id"):
                QtWidgets.QMessageBox.warning(self, "Error", "Select a customer first.")
                return

            # Auto-create a new order
            new_order_id = OrderDB.add_order(self.selected_customer_id, notes="New Order")
            if not new_order_id:
                QtWidgets.QMessageBox.critical(self, "Error", "Failed to add order.")
                return

            # Set as selected order
            self.selected_order_id = new_order_id
            self.load_orders()

            # Find the row of the new order and select it
            for row in range(self.order_table.rowCount()):
                if int(self.order_table.item(row, 0).text()) == new_order_id:
                    self.order_table.selectRow(row)
                    break

        except Exception as e:
            print(f"[ERROR] Add order failed: {e}")

    def delete_order(self):
        try:
            row = self.order_table.currentRow()
            if row < 0:
                QtWidgets.QMessageBox.warning(self, "Error", "Select an order first.")
                return
            order_id = int(self.order_table.item(row, 0).text())
            confirm = QtWidgets.QMessageBox.question(
                self, "Confirm", f"Delete order #{order_id}?",
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
            )
            if confirm == QtWidgets.QMessageBox.Yes:
                OrderDB.delete_order(order_id)
                self.load_orders()
        except Exception as e:
            print(f"[ERROR] Delete order failed: {e}")
    def update_order(self):
        try:
            row = self.order_table.currentRow()
            if row < 0:
                QMessageBox.warning(self, "Error", "Select an order first.")
                return

            order_id = int(self.order_table.item(row, 0).text())

            # Status options
            status_options = [
                "New Order",
                "Invoice Sent",
                "Invoice Received",
                "BOM Completed",
                "Order in Progress",
                "Order Completed",
                "Shipped",
                "Closed"
            ]

            status, ok = QInputDialog.getItem(
                self,
                "Update Order",
                "Select new status:",
                status_options,
                0,  # default index
                False  # not editable
            )

            if ok and status:
                OrderDB.update_order(order_id, status=status)
                self.load_orders()
                QMessageBox.information(self, "Success", f"Order updated to '{status}'.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Update order failed:\n{e}")
            import traceback
            print("[DEBUG] Traceback:\n", traceback.format_exc())
# ---------------- Right Panel  -------------------------------------------------------------------------

    # ---------------- Right Panel -row 1 Loading Recipes -------------------------------------------------------------------------
    def remove_line_item(self):
        """UI handler for deleting the selected line item."""
        try:
            row = self.lineitem_table.currentRow()
            if row < 0:
                QtWidgets.QMessageBox.warning(self, "Error", "Select a line item first.")
                return

            lineitem_id = int(self.lineitem_table.item(row, 0).text())
            confirm = QtWidgets.QMessageBox.question(
                self,
                "Confirm",
                f"Delete line item #{lineitem_id}?",
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
            )
            if confirm == QtWidgets.QMessageBox.Yes:
                LineItemDB.delete_order_item(lineitem_id)
                self.load_line_items()
        except Exception as e:
            print(f"[ERROR] UI remove_line_item failed: {e}")
    def add_line_item(self):
            try:
                if not hasattr(self, "selected_order_id") or self.selected_order_id is None:
                    QtWidgets.QMessageBox.warning(self, "Error", "Select an order first.")
                    return

                # Pick recipe
                recipes = LineItemDB.get_all_recipes()
                recipe_names = [r[1] for r in recipes]
                recipe_choice, ok = QtWidgets.QInputDialog.getItem(self, "Select Recipe", "Recipe:", recipe_names, 0, False)
                if not ok: return

                # Pick quantity
                quantity, ok = QtWidgets.QInputDialog.getInt(self, "Quantity", "Enter quantity:", 1, 1)
                if not ok: return

                recipe_id = next(r[0] for r in recipes if r[1] == recipe_choice)

                # Insert into DB
                LineItemDB.add_order_item(self.selected_order_id, recipe_id, quantity)
                self.load_line_items()
                self.stock_check_panel.load_stock(self.selected_order_id)  # Refresh summary and tree
                QtWidgets.QMessageBox.information(self, "Success", f"Added {quantity} x {recipe_choice}")

            except Exception as e:
                print(f"[ERROR] Adding line item failed: {e}")

    def load_line_items(self):
        """Load all line items for the selected order into the table."""
        try:
            if not hasattr(self, "selected_order_id"):
                return
            self.lineitem_table.setRowCount(0)
            items = OrderDB.get_order_items(self.selected_order_id)  # returns list of tuples
            for item in items:
                row = self.lineitem_table.rowCount()
                self.lineitem_table.insertRow(row)
                self.lineitem_table.setItem(row, 0, QtWidgets.QTableWidgetItem(str(item[0])))  # Line Item ID
                self.lineitem_table.setItem(row, 1, QtWidgets.QTableWidgetItem(str(item[2])))  # Recipe ID or name
                self.lineitem_table.setItem(row, 2, QtWidgets.QTableWidgetItem(str(item[3])))  # Quantity
                self.lineitem_table.setItem(row, 3, QtWidgets.QTableWidgetItem(str(item[4])))  # Unit / Price
        except Exception as e:
            print(f"[ERROR] Loading line items failed: {e}")
    def load_line_items(self):
        try:
            if not hasattr(self, "selected_order_id"):
                return
            self.lineitem_table.setRowCount(0)
            items = LineItemDB.get_order_items(self.selected_order_id)
            for item in items:
                row = self.lineitem_table.rowCount()
                self.lineitem_table.insertRow(row)
                self.lineitem_table.setItem(row, 0, QtWidgets.QTableWidgetItem(str(item[0])))  # Line Item ID
                self.lineitem_table.setItem(row, 1, QtWidgets.QTableWidgetItem(str(item[2])))  # Recipe Name
                self.lineitem_table.setItem(row, 2, QtWidgets.QTableWidgetItem(str(item[3])))  # Quantity
        except Exception as e:
            print(f"[ERROR] Loading line items failed: {e}")
    def update_line_item(self):
        """Update quantity of the selected line item."""
        try:
            row = self.lineitem_table.currentRow()
            if row < 0:
                QtWidgets.QMessageBox.warning(self, "Error", "Select a line item first.")
                return

            lineitem_id = int(self.lineitem_table.item(row, 0).text())
            current_qty = int(self.lineitem_table.item(row, 2).text())

            new_qty, ok = QtWidgets.QInputDialog.getInt(
                self, "Update Quantity", "Enter new quantity:", current_qty, 1
            )
            if not ok:
                return

            try:
                success = LineItemDB.update_order_item(lineitem_id, new_qty)
                if success:
                    QtWidgets.QMessageBox.information(
                        self, "Success", f"Line item updated to {new_qty}."
                    )
                else:
                    QtWidgets.QMessageBox.critical(
                        self, "Error", "Failed to update line item."
                    )
            except ValueError as ve:
                QtWidgets.QMessageBox.warning(self, "Invalid Quantity", str(ve))

            self.load_line_items()
            self.stock_check_panel.load_stock(self.selected_order_id)  # Refresh summary and tree

        except Exception as e:
            print(f"[ERROR] Updating line item failed: {e}")
            QtWidgets.QMessageBox.critical(self, "Error", f"Unexpected error:\n{e}")

    def delete_line_item(self):
        """Delete the currently selected line item."""
        try:
            row = self.lineitem_table.currentRow()
            if row < 0:
                QtWidgets.QMessageBox.warning(self, "Error", "Select a line item first.")
                return

            lineitem_id = int(self.lineitem_table.item(row, 0).text())
            confirm = QtWidgets.QMessageBox.question(
                self, "Confirm", f"Delete line item #{lineitem_id}?",
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
            )
            if confirm == QtWidgets.QMessageBox.Yes:
                LineItemDB.delete_order_item(lineitem_id)
                self.load_line_items()
                self.stock_check_panel.load_stock(self.selected_order_id)  # Refresh summary and tree
        except Exception as e:
            print(f"[ERROR] Deleting line item failed: {e}")
                  
    def on_order_selected(self, row, column, prev_row, prev_column):
        if row < 0:
            self.selected_order_id = None
            self.add_lineitem_btn.setEnabled(False)
            self.edit_lineitem_btn.setEnabled(False)
            self.delete_lineitem_btn.setEnabled(False)
            self.lineitem_table.setRowCount(0)
            return

        self.selected_order_id = int(self.order_table.item(row, 0).text())
        self.add_lineitem_btn.setEnabled(True)
        self.edit_lineitem_btn.setEnabled(True)
        self.delete_lineitem_btn.setEnabled(True)
        self.load_line_items()
        self.stock_check_panel.load_stock(self.selected_order_id)  # <-- fixed here

        # --- PRINT ALL INGREDIENTS FOR THIS ORDER ---
        print(f"\n[DEBUG] Ingredients for Order {self.selected_order_id}:")
        items = LineItemDB.get_order_items(self.selected_order_id)
        for item in items:
            lineitem_id = item[0]
            recipe_id = LineItemDB.get_recipe_id(lineitem_id)
            print(f"  LineItem {lineitem_id} (Recipe ID: {recipe_id}):")
            ingredients = RecipeDB.get_recipe_ingredients(recipe_id)
            for ing in ingredients:
                print("    ", ing)
    # ---------------- Right Panel -row 2 -------------------------------------------------------------------------
    def _status(self, required, available):
        if available >= required:
            return "✅ Enough"
        elif available > 0:
            return "⚠️ Low"
        else:
            return "❌ Missing"
    def _color_row(self, item, status):
        if "Enough" in status:
            color = QtGui.QColor(144, 238, 144)  # light green
        elif "Low" in status:
            color = QtGui.QColor(255, 165, 0)    # orange
        else:
            color = QtGui.QColor(255, 99, 71)    # red
        for col in range(item.columnCount()):
            item.setBackground(col, color)
    def _color_row_table(self, row, status):
        if "Enough" in status:
            color = QtGui.QColor(144, 238, 144)
        elif "Low" in status:
            color = QtGui.QColor(255, 165, 0)
        else:
            color = QtGui.QColor(255, 99, 71)
        for col in range(self.summary_table.columnCount()):
            self.summary_table.item(row, col).setBackground(color)


# ---------------- Run demo ----------------
if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    window = CustomerOrdersPopup()
    window.show()
    app.exec_()
