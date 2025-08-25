from PyQt5 import QtWidgets
from order_dialog import AddEditOrderDialog
from order_db import OrderDB

class OrdersPopup(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Orders")
        self.resize(600, 400)
        layout = QtWidgets.QVBoxLayout()

        self.table = QtWidgets.QTableWidget()
        layout.addWidget(self.table)

        btn_layout = QtWidgets.QHBoxLayout()
        self.add_btn = QtWidgets.QPushButton("Add Order")
        self.edit_btn = QtWidgets.QPushButton("Edit Order")
        self.delete_btn = QtWidgets.QPushButton("Delete Order")
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.edit_btn)
        btn_layout.addWidget(self.delete_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

        self.add_btn.clicked.connect(self.add_order)
        # edit_btn and delete_btn can be implemented similarly

        self.load_orders()

    def load_orders(self):
        try:
            orders = OrderDB.get_all_orders()
            self.table.setRowCount(len(orders))
            self.table.setColumnCount(4)
            self.table.setHorizontalHeaderLabels(["ID", "Customer", "Date", "Notes"])
            for row, order in enumerate(orders):
                self.table.setItem(row, 0, QtWidgets.QTableWidgetItem(str(order["ID"])))
                self.table.setItem(row, 1, QtWidgets.QTableWidgetItem(order["customer_name"]))
                self.table.setItem(row, 2, QtWidgets.QTableWidgetItem(str(order["order_date"])))
                self.table.setItem(row, 3, QtWidgets.QTableWidgetItem(order.get("notes", "")))
        except Exception as e:
            print(f"Error loading orders: {e}")

    def add_order(self):
        dialog = AddEditOrderDialog(self)
        if dialog.exec_():
            self.load_orders()
