from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QInputDialog, QMessageBox

from customer_db import CustomerDB
from order_db import OrderDB
from line_item_db import LineItemDB




ALLOWED_ORDER_STATUSES = [
    "Invoice Sent",
    "Invoice Received",
    "BOM Completed",
    "Order in Progress",
    "Order Completed",
    "Shipped",
    "Closed"
]

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
        self.resize(1000, 600)

        # ---------------- MAIN LAYOUT ----------------
        main_layout = QtWidgets.QHBoxLayout(self)

        # ========== LEFT PANEL ==========
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

        # ========== MIDDLE PANEL ==========
        middle_layout = QtWidgets.QVBoxLayout()

        # --- Customer Profile ---
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

        # Auto-update customer fields
        self.name_input.textChanged.connect(lambda: self.update_customer_field('name'))
        self.phone_input.textChanged.connect(lambda: self.update_customer_field('phone'))
        self.email_input.textChanged.connect(lambda: self.update_customer_field('email'))
        self.subscribed_checkbox.stateChanged.connect(lambda _: self.update_customer_field('subscribed'))
        self.address_input.textChanged.connect(lambda: self.update_customer_field('address'))
        self.notes_input.textChanged.connect(lambda: self.update_customer_field('notes'))

        # --- Orders ---
        self.orders_group = QtWidgets.QGroupBox("Orders")
        orders_layout = QtWidgets.QVBoxLayout()
        self.order_table = QtWidgets.QTableWidget()
        self.order_table.setColumnCount(3)
        self.order_table.setHorizontalHeaderLabels(["Order ID", "Date", "Status"])
        self.order_table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        orders_layout.addWidget(self.order_table)

        # Buttons for orders
        self.add_order_btn = QtWidgets.QPushButton("Add Order")
        self.edit_order_btn = QtWidgets.QPushButton("Edit Order")
        self.delete_order_btn = QtWidgets.QPushButton("Delete Order")
        orders_layout.addWidget(self.add_order_btn)
        orders_layout.addWidget(self.edit_order_btn)
        orders_layout.addWidget(self.delete_order_btn)

        self.orders_group.setLayout(orders_layout)
        middle_layout.addWidget(self.orders_group, 2)

        # Bind order actions
        self.add_order_btn.clicked.connect(self.add_order)
        self.edit_order_btn.clicked.connect(self.update_order)
        self.delete_order_btn.clicked.connect(self.delete_order)

        # Detect order selection
        self.order_table.currentCellChanged.connect(self.on_order_selected)

        # ========== RIGHT PANEL ==========
        right_layout = QtWidgets.QVBoxLayout()
        right_layout.addWidget(QtWidgets.QLabel("Line Items"))

        # --- Line Items Table ---
        self.lineitem_table = QtWidgets.QTableWidget()
        self.lineitem_table.setColumnCount(3)
        self.lineitem_table.setHorizontalHeaderLabels(["Line Item ID", "Product/Recipe", "Qty"])
        self.lineitem_table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        right_layout.addWidget(self.lineitem_table)

        self.lineitem_table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        right_layout.addWidget(self.lineitem_table)

        # --- Line Item Buttons ---
        self.add_lineitem_btn = QtWidgets.QPushButton("Add Line Item")
        self.edit_lineitem_btn = QtWidgets.QPushButton("Edit Line Item")
        self.delete_lineitem_btn = QtWidgets.QPushButton("Delete Line Item")
        right_layout.addWidget(self.add_lineitem_btn)
        right_layout.addWidget(self.edit_lineitem_btn)
        right_layout.addWidget(self.delete_lineitem_btn)
        self.add_lineitem_btn.setEnabled(False)
        self.edit_lineitem_btn.setEnabled(False)
        self.delete_lineitem_btn.setEnabled(False)

        # Bind actions
        self.add_lineitem_btn.clicked.connect(self.add_line_item)
        self.edit_lineitem_btn.clicked.connect(self.update_line_item)
        self.delete_lineitem_btn.clicked.connect(self.delete_line_item)



        # ========== ADD PANELS TO MAIN LAYOUT ==========
        main_layout.addLayout(left_layout, 1)
        main_layout.addLayout(middle_layout, 2)
        main_layout.addLayout(right_layout, 2)

        # Load customers into UI
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
        except Exception as e:
            print(f"[ERROR] Deleting line item failed: {e}")
    def on_order_selected(self, row, column, prev_row, prev_column):
        """Triggered when the user selects an order in the table."""
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

    # ---------------- Right Panel -row 2 -------------------------------------------------------------------------







# ---------------- Run demo ----------------
if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    window = CustomerOrdersPopup()
    window.show()
    app.exec_()
