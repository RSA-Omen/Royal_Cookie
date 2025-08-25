from PyQt5 import QtWidgets
from customer_db import CustomerDB

class CustomersPopup(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Manage Customers")
        self.resize(700, 400)

        # --- Inputs ---
        form_layout = QtWidgets.QHBoxLayout()
        self.name_input = QtWidgets.QLineEdit(); self.name_input.setPlaceholderText("Name")
        self.phone_input = QtWidgets.QLineEdit(); self.phone_input.setPlaceholderText("Phone")
        self.email_input = QtWidgets.QLineEdit(); self.email_input.setPlaceholderText("Email")
        self.subscribed_checkbox = QtWidgets.QCheckBox("Subscribed")
        self.address_input = QtWidgets.QLineEdit(); self.address_input.setPlaceholderText("Address")
        self.notes_input = QtWidgets.QLineEdit(); self.notes_input.setPlaceholderText("Notes")

        form_layout.addWidget(self.name_input)
        form_layout.addWidget(self.phone_input)
        form_layout.addWidget(self.email_input)
        form_layout.addWidget(self.subscribed_checkbox)
        form_layout.addWidget(self.address_input)
        form_layout.addWidget(self.notes_input)

        # --- Buttons ---
        btn_layout = QtWidgets.QHBoxLayout()
        self.add_btn = QtWidgets.QPushButton("Add")
        self.update_btn = QtWidgets.QPushButton("Update")
        self.delete_btn = QtWidgets.QPushButton("Delete")
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.update_btn)
        btn_layout.addWidget(self.delete_btn)

        # --- Table ---
        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(
            ["ID", "Name", "Phone", "Email", "Subscribed", "Address", "Notes", "Created At"]
        )
        self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.table.cellClicked.connect(self.fill_form)

        # --- Layout ---
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addLayout(form_layout)
        main_layout.addLayout(btn_layout)
        main_layout.addWidget(self.table)

        # --- Connect buttons ---
        self.add_btn.clicked.connect(self.add_customer)
        self.update_btn.clicked.connect(self.update_customer)
        self.delete_btn.clicked.connect(self.delete_customer)

        self.refresh_table()

    # ---------------- Methods ----------------
    def refresh_table(self):
        self.table.setRowCount(0)
        customers = CustomerDB.get_customers()
        for row_num, c in enumerate(customers):
            self.table.insertRow(row_num)
            for col, val in enumerate(c):
                if col == 4:  # subscribed
                    val = "Yes" if val else "No"
                self.table.setItem(row_num, col, QtWidgets.QTableWidgetItem(str(val)))

    def fill_form(self, row, _col):
        self.selected_id = int(self.table.item(row, 0).text())
        self.name_input.setText(self.table.item(row, 1).text())
        self.phone_input.setText(self.table.item(row, 2).text())
        self.email_input.setText(self.table.item(row, 3).text())
        self.subscribed_checkbox.setChecked(self.table.item(row, 4).text() == "Yes")
        self.address_input.setText(self.table.item(row, 5).text())
        self.notes_input.setText(self.table.item(row, 6).text())

    def add_customer(self):
        CustomerDB.add_customer(
            self.name_input.text(),
            self.phone_input.text(),
            self.email_input.text(),
            1 if self.subscribed_checkbox.isChecked() else 0,
            self.address_input.text(),
            self.notes_input.text()
        )
        self.refresh_table()

    def update_customer(self):
        if hasattr(self, "selected_id"):
            CustomerDB.update_customer(
                self.selected_id,
                self.name_input.text(),
                self.phone_input.text(),
                self.email_input.text(),
                1 if self.subscribed_checkbox.isChecked() else 0,
                self.address_input.text(),
                self.notes_input.text()
            )
            self.refresh_table()

    def delete_customer(self):
        if hasattr(self, "selected_id"):
            CustomerDB.delete_customer(self.selected_id)
            self.refresh_table()
