from PyQt5 import QtWidgets, QtCore
from customer_db import CustomerDB  # your existing DB

class CustomerOrdersPopup(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Customer Orders Manager")
        self.resize(1000, 600)

        self.updating_fields = False

        # --- Main layout ---
        main_layout = QtWidgets.QHBoxLayout(self)

        # ---------------- Left Panel: Customers ----------------
        left_layout = QtWidgets.QVBoxLayout()
        left_layout.addWidget(QtWidgets.QLabel("Customers"))

        self.customer_list = QtWidgets.QListWidget()
        self.customer_list.currentItemChanged.connect(self.on_customer_selected)
        left_layout.addWidget(self.customer_list)

        for text in ["Add Customer", "Edit Customer", "Delete Customer"]:
            btn = QtWidgets.QPushButton(text)
            left_layout.addWidget(btn)

        # ---------------- Middle Panel (split vertically) ----------------
        middle_layout = QtWidgets.QVBoxLayout()

        # --- Top: Customer Profile ---
        self.profile_group = QtWidgets.QGroupBox("Customer Profile")
        profile_layout = QtWidgets.QFormLayout()

        self.name_input = QtWidgets.QLineEdit()
        self.phone_input = QtWidgets.QLineEdit()
        self.email_input = QtWidgets.QLineEdit()
        self.subscribed_checkbox = QtWidgets.QCheckBox()
        self.address_input = QtWidgets.QLineEdit()
        self.notes_input = QtWidgets.QLineEdit()

        profile_layout.addRow("Name:", self.name_input)
        profile_layout.addRow("Phone:", self.phone_input)
        profile_layout.addRow("Email:", self.email_input)
        profile_layout.addRow("Subscribed:", self.subscribed_checkbox)
        profile_layout.addRow("Address:", self.address_input)
        profile_layout.addRow("Notes:", self.notes_input)

        self.profile_group.setLayout(profile_layout)
        middle_layout.addWidget(self.profile_group, 1)

        # Connect field changes to DB updates
        self.name_input.textChanged.connect(lambda: self.update_customer_field('name'))
        self.phone_input.textChanged.connect(lambda: self.update_customer_field('phone'))
        self.email_input.textChanged.connect(lambda: self.update_customer_field('email'))
        self.subscribed_checkbox.stateChanged.connect(lambda _: self.update_customer_field('subscribed'))
        self.address_input.textChanged.connect(lambda: self.update_customer_field('address'))
        self.notes_input.textChanged.connect(lambda: self.update_customer_field('notes'))

        # --- Bottom: Orders ---
        self.orders_group = QtWidgets.QGroupBox("Orders")
        orders_layout = QtWidgets.QVBoxLayout()
        self.order_table = QtWidgets.QTableWidget()
        self.order_table.setColumnCount(3)
        self.order_table.setHorizontalHeaderLabels(["Order ID", "Date", "Status"])
        self.order_table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        orders_layout.addWidget(self.order_table)

        for text in ["Add Order", "Edit Order", "Delete Order"]:
            btn = QtWidgets.QPushButton(text)
            orders_layout.addWidget(btn)

        self.orders_group.setLayout(orders_layout)
        middle_layout.addWidget(self.orders_group, 2)

        # ---------------- Right Panel: Line Items ----------------
        right_layout = QtWidgets.QVBoxLayout()
        right_layout.addWidget(QtWidgets.QLabel("Line Items"))

        self.lineitem_table = QtWidgets.QTableWidget()
        self.lineitem_table.setColumnCount(4)
        self.lineitem_table.setHorizontalHeaderLabels(["Line Item ID", "Product/Recipe", "Qty", "Unit"])
        self.lineitem_table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        right_layout.addWidget(self.lineitem_table)

        for text in ["Add Line Item", "Edit Line Item", "Delete Line Item"]:
            btn = QtWidgets.QPushButton(text)
            right_layout.addWidget(btn)

        # ---------------- Combine layouts ----------------
        main_layout.addLayout(left_layout, 1)
        main_layout.addLayout(middle_layout, 2)
        main_layout.addLayout(right_layout, 2)

        # --- Load customers ---
        self.refresh_customers()

    # ---------------- Customer methods ----------------
    def update_customer_field(self, field):
        if not hasattr(self, "selected_id") or self.updating_fields:
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

        if field in value_map:
            CustomerDB.update_customer(cid, **{field: value_map[field]})

            # --- Update the displayed item in the list ---
            for i in range(self.customer_list.count()):
                item = self.customer_list.item(i)
                if item.data(QtCore.Qt.UserRole) == cid:
                    # Update the text only
                    item.setText(f"{self.name_input.text()} ({self.phone_input.text()})")
                    break

    def refresh_customers(self):
        self.customer_list.clear()
        self.customers = CustomerDB.get_customers()
        for c in self.customers:
            item = QtWidgets.QListWidgetItem(f"{c[1]} ({c[2]})")  # Name (Phone)
            item.setData(QtCore.Qt.UserRole, c[0])
            self.customer_list.addItem(item)

    def on_customer_selected(self, current, previous):
        if not current:
            return

        cid = current.data(QtCore.Qt.UserRole)
        customer = next((c for c in self.customers if c[0] == cid), None)
        if not customer:
            return

        self.updating_fields = True
        self.selected_id = cid
        self.name_input.setText(customer[1])
        self.phone_input.setText(customer[2])
        self.email_input.setText(customer[3])
        self.subscribed_checkbox.setChecked(customer[4] == 1)
        self.address_input.setText(customer[5])
        self.notes_input.setText(customer[6])
        self.updating_fields = False

        # Demo: populate orders
        self.order_table.setRowCount(0)
        for i in range(2):
            row = self.order_table.rowCount()
            self.order_table.insertRow(row)
            self.order_table.setItem(row, 0, QtWidgets.QTableWidgetItem(f"Order {i+1}"))
            self.order_table.setItem(row, 1, QtWidgets.QTableWidgetItem("2025-08-25"))
            self.order_table.setItem(row, 2, QtWidgets.QTableWidgetItem("Pending"))

        self.lineitem_table.setRowCount(0)  # clear line items on customer switch

# ---------------- Run demo ----------------
if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    window = CustomerOrdersPopup()
    window.show()
    app.exec_()
