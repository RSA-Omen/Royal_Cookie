from PyQt5 import QtWidgets, QtCore

class FinancialDashboardUI(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Financial Dashboard")
        self.resize(600, 400)


        layout = QtWidgets.QVBoxLayout(self)

        # Date range selectors
        date_layout = QtWidgets.QHBoxLayout()
        date_layout.addWidget(QtWidgets.QLabel("Start Date:"))
        self.start_date = QtWidgets.QDateEdit(QtCore.QDate.currentDate().addMonths(-1))
        self.start_date.setCalendarPopup(True)
        date_layout.addWidget(self.start_date)
        date_layout.addWidget(QtWidgets.QLabel("End Date:"))
        self.end_date = QtWidgets.QDateEdit(QtCore.QDate.currentDate())
        self.end_date.setCalendarPopup(True)
        date_layout.addWidget(self.end_date)
        self.refresh_btn = QtWidgets.QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.update_dashboard)
        date_layout.addWidget(self.refresh_btn)
        layout.addLayout(date_layout)

        # Financial metrics
        self.sales_label = QtWidgets.QLabel("Total Sales: R0.00")
        self.cogs_label = QtWidgets.QLabel("Cost of Goods Sold: R0.00")
        self.gross_profit_label = QtWidgets.QLabel("Gross Profit: R0.00")
        layout.addWidget(self.sales_label)
        layout.addWidget(self.cogs_label)
        layout.addWidget(self.gross_profit_label)

    def update_dashboard(self):
        from order_db import OrderDB
        from line_item_db import LineItemDB
        from recipe_db import RecipeDB
        import datetime

        # Get date range from pickers
        start = self.start_date.date().toPyDate()
        end = self.end_date.date().toPyDate()

        # Query all orders in date range
        orders = OrderDB.get_all_orders()
        total_sales = 0.0
        total_cogs = 0.0

        for order in orders:
            # order: (id, customer_name, status, order_date, delivery_date, total_amount, notes)
            order_id = order[0]
            order_date = order[3]
            try:
                order_date_obj = datetime.datetime.strptime(order_date, "%Y-%m-%d").date()
            except Exception:
                continue
            if not (start <= order_date_obj <= end):
                continue
            total_amount = order[5] if order[5] is not None else 0.0
            total_sales += total_amount

            # Calculate COGS for this order
            items = LineItemDB.get_order_items(order_id)
            for item in items:
                # item: (lineitem_id, order_id, recipe_name, quantity)
                recipe_id = LineItemDB.get_recipe_id(item[0])
                qty = item[3]
                # Get output_quantity for this recipe
                recipe = None
                for r in RecipeDB.get_all_recipes():
                    if r[0] == recipe_id:
                        recipe = r
                        break
                output_quantity = recipe[2] if recipe and recipe[2] is not None else 1
                batch_cost = RecipeDB.calculate_cost_per_batch(recipe_id)
                # COGS per unit * total units sold
                unit_cost = batch_cost / output_quantity if output_quantity else batch_cost
                total_cogs += unit_cost * qty * output_quantity

        gross_profit = total_sales - total_cogs
        self.sales_label.setText(f"Total Sales: R{total_sales:.2f}")
        self.cogs_label.setText(f"Cost of Goods Sold: R{total_cogs:.2f}")
        self.gross_profit_label.setText(f"Gross Profit: R{gross_profit:.2f}")

    # Methods to update dashboard values will be added later
