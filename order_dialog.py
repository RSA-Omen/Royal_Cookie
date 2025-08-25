from PyQt5 import QtWidgets
from db import get_connection
from customer_db import CustomerDB
from order_db import OrderDB
from datetime import datetime

class AddEditOrderDialog(QtWidgets.QDialog):
    def __init__(self, parent=None, order=None):
        super().__init__(parent)
        self.setWindowTitle("Add / Edit Order")
        self.resize(400, 200)
        self.order = order  # None for new order
        self.customers = []

        layout = QtWidgets.QVBoxLayout()

        # Customer selection
        cust_layout = QtWidgets.QHBoxLayout()
        cust_label = QtWidgets.QLabel("Customer:")
        self.customer_combo = QtWidgets.QComboBox()
        cust_layout.addWidget(cust_label)
        cust_layout.addWidget(self.customer_combo)
        layout.addLayout(cust_layout)

        # Order date
        date_layout = QtWidgets.QHBoxLayout()
        date_label = QtWidgets.QLabel("Order Date:")
        self.date_edit = QtWidgets.QDateEdit(datetime.now())
        self.date_edit.setCalendarPopup(True)
        date_layout.addWidget(date_label)
        date_layout.addWidget(self.date_edit)
        layout.addLayout(date_layout)

        # Notes
        notes_layout = QtWidgets.QHBoxLayout()
        notes_label = QtWidgets.QLabel("Notes:")
        self.notes_edit = QtWidgets.QLineEdit()
        notes_layout.addWidget(notes_label)
        notes_layout.addWidget(self.notes_edit)
        layout.addLayout(notes_layout)

        # Buttons
        btn_layout = QtWidgets.QHBoxLayout()
        self.save_btn = QtWidgets.QPushButton("Save")
        self.cancel_btn = QtWidgets.QPushButton("Cancel")
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

        # Signals
        self.save_btn.clicked.connect(self.save_order)
        self.cancel_btn.clicked.connect(self.close)

        # Load customers safely
        self.load_customers()

        # If editing, populate fields
        if self.order:
            self.populate_fields()

    def load_customers(self):
        try:
            raw_customers = CustomerDB.get_all_customers()
            self.customers = []
            self.customer_combo.clear()
            for c in raw_customers:
                try:
                    cust_id = c["ID"]
                    cust_name = c["Name"]
                except Exception:
                    cust_id = c[0]
                    cust_name = c[1]
                self.customers.append({"ID": cust_id, "Name": cust_name})
                self.customer_combo.addItem(cust_name, cust_id)
        except Exception as e:
            print(f"Error loading customers: {e}")
            self.customers = []

    def populate_fields(self):
        try:
            cust_id = self.order["customer_id"]
            index = next((i for i, c in enumerate(self.customers) if c["ID"] == cust_id), 0)
            self.customer_combo.setCurrentIndex(index)
        except Exception as e:
            print(f"Error setting customer: {e}")

        try:
            self.date_edit.setDate(self.order["order_date"])
        except Exception as e:
            print(f"Error setting date: {e}")

        try:
            self.notes_edit.setText(self.order.get("notes", ""))
        except Exception as e:
            print(f"Error setting notes: {e}")

    def save_order(self):
        try:
            cust_index = self.customer_combo.currentIndex()
            customer_id = self.customer_combo.itemData(cust_index)
            order_date = self.date_edit.date().toPyDate()
            notes = self.notes_edit.text()

            if self.order:
                # Update existing
                OrderDB.update_order(self.order["ID"], customer_id, order_date, notes)
            else:
                # Add new
                OrderDB.add_order(customer_id, order_date, notes)

            self.accept()
        except Exception as e:
            print(f"Error saving order: {e}")
