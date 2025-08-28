from order_db import OrderDB
from PyQt5 import QtWidgets,QtGui
from line_item_db import LineItemDB
from recipe_db import RecipeDB
from Stock_db import IngredientStockDB
from reservation_db import ReservationDB


class ProductionController:
    def __init__(self, ui):
        print("ProductionController initialized")
        self.ui = ui
        self.load_orders()
        self.ui.orders_table.itemSelectionChanged.connect(self.on_order_selected)
        self.ui.reserve_btn.clicked.connect(self.reserve_ingredients)
        self.ui.release_btn.clicked.connect(self.release_reservations)
        self.ui.status_btn.clicked.connect(self.change_order_status)
        self.ui.notes_text.focusOutEvent = self.save_production_note_on_focus_out

    def load_orders(self):
        orders = OrderDB.get_all_orders()
        table = self.ui.orders_table
        table.setRowCount(0)
        for row_idx, order in enumerate(orders):
            table.insertRow(row_idx)
            # order: (id, customer_name, status, order_date, delivery_date, total_amount, notes)
            table.setItem(row_idx, 0, QtWidgets.QTableWidgetItem(str(order[0])))  # Order ID
            table.setItem(row_idx, 1, QtWidgets.QTableWidgetItem(order[1]))       # Customer
            table.setItem(row_idx, 2, QtWidgets.QTableWidgetItem(order[2]))       # Status
            table.setItem(row_idx, 3, QtWidgets.QTableWidgetItem(order[4] or "")) # Date of delivery
            table.setItem(row_idx, 4, QtWidgets.QTableWidgetItem(str(order[5])))  # Total
            table.setItem(row_idx, 5, QtWidgets.QTableWidgetItem(order[6] or "")) # Notes

    def on_order_selected(self):
        selected = self.ui.orders_table.currentRow()
        if selected < 0:
            self.ui.lineitems_table.setRowCount(0)
            return
        order_id = int(self.ui.orders_table.item(selected, 0).text())
        self.load_line_items(order_id)
        self.load_ingredients(order_id)

    def load_line_items(self, order_id):
        items = LineItemDB.get_order_items(order_id)
        table = self.ui.lineitems_table
        table.setRowCount(0)
        for row_idx, item in enumerate(items):
            table.insertRow(row_idx)
            table.setItem(row_idx, 0, QtWidgets.QTableWidgetItem(str(item[0])))  # Line Item ID
            table.setItem(row_idx, 1, QtWidgets.QTableWidgetItem(item[2]))       # Recipe Name
            table.setItem(row_idx, 2, QtWidgets.QTableWidgetItem(str(item[3])))  # Quantity
        # No row coloring for line items as per user request
               
    def load_ingredients(self, order_id):
        table = self.ui.ingredients_table
        table.setRowCount(0)
        items = LineItemDB.get_order_items(order_id)
        ingredient_totals = {}  # key: (metadata_id, ing_name, unit), value: total required

        for item in items:
            lineitem_id, order_id, recipe_name, quantity = item
            recipe_id = LineItemDB.get_recipe_id(lineitem_id)
            if not recipe_id:
                continue
            ingredients = RecipeDB.get_recipe_ingredients(recipe_id)
            for ing in ingredients:
                metadata_id = ing[2]
                ing_name = ing[5]
                per_recipe_amt = ing[3]
                unit = ing[4]
                required = per_recipe_amt * quantity

                key = (metadata_id, ing_name, unit)
                if key not in ingredient_totals:
                    ingredient_totals[key] = 0
                ingredient_totals[key] += required

        stock_db = IngredientStockDB()

        for row_idx, ((metadata_id, ing_name, unit), total_required) in enumerate(ingredient_totals.items()):
            reserved = ReservationDB.get_reserved_qty_for_order(order_id, metadata_id)
            available_physical = stock_db.get_available_stock(metadata_id)
            reserved_global = ReservationDB.get_reserved_qty(metadata_id)
            available = max(0, (available_physical or 0) - (reserved_global or 0))
            shortage = max(0, total_required - (available - reserved))

            table.insertRow(row_idx)
            table.setItem(row_idx, 0, QtWidgets.QTableWidgetItem(str(ing_name)))
            table.setItem(row_idx, 1, QtWidgets.QTableWidgetItem(f"{total_required} {unit}"))
            table.setItem(row_idx, 2, QtWidgets.QTableWidgetItem(f"{reserved} {unit}"))
            table.setItem(row_idx, 3, QtWidgets.QTableWidgetItem(f"{available} {unit}"))
            table.setItem(row_idx, 4, QtWidgets.QTableWidgetItem(f"{shortage} {unit}"))
            table.setItem(row_idx, 5, QtWidgets.QTableWidgetItem(""))

            # Updated coloring logic for partial reservations
            if reserved >= total_required:
                color = QtGui.QColor(144, 238, 144)  # green: fully reserved
            elif reserved > 0:
                color = QtGui.QColor(255, 255, 102)   # yellow: partially reserved
            else:
                color = QtGui.QColor(255, 99, 71)    # red: not reserved

            for col in range(table.columnCount()):
                cell_item = table.item(row_idx, col)
                if cell_item is not None:
                    cell_item.setBackground(color)
        
    def change_order_status(self):
        selected = self.ui.orders_table.currentRow()
        if selected < 0:
            return
        order_id = int(self.ui.orders_table.item(selected, 0).text())
        statuses = ["New", "Awaiting Stock", "Reserved", "In Production", "Ready for Delivery", "Delivered", "Cancelled"]
        status, ok = QtWidgets.QInputDialog.getItem(self.ui, "Change Order Status", "Select new status:", statuses, 0, False)
        if ok and status:
            OrderDB.update_order(order_id, status=status)
            self.load_orders()

    def save_production_note_on_focus_out(self, event):
        selected = self.ui.orders_table.currentRow()
        if selected < 0:
            return
        order_id = int(self.ui.orders_table.item(selected, 0).text())
        note = self.ui.notes_text.toPlainText()
        OrderDB.update_order(order_id, notes=note)
        event.accept()

    def reserve_ingredients(self):
        print("running a reservation")
        selected = self.ui.orders_table.currentRow()
        if selected < 0:
            QtWidgets.QMessageBox.warning(self.ui, "No Order Selected", "Please select an order to reserve ingredients for.")
            return
        order_id = int(self.ui.orders_table.item(selected, 0).text())

        # Get required ingredients for this order
        items = LineItemDB.get_order_items(order_id)
        # Build a list of all (lineitem_id, metadata_id, qty_needed) for this order
        reservation_requests = []
        for item in items:
            lineitem_id, order_id, recipe_name, quantity = item
            recipe_id = LineItemDB.get_recipe_id(lineitem_id)
            if not recipe_id:
                continue
            ingredients = RecipeDB.get_recipe_ingredients(recipe_id)
            for ing in ingredients:
                metadata_id = ing[2]
                per_recipe_amt = ing[3]
                required = per_recipe_amt * quantity
                already_reserved = ReservationDB.get_reserved_qty_for_order(order_id, metadata_id)
                to_reserve = required - already_reserved
                if to_reserve > 0:
                    reservation_requests.append((lineitem_id, metadata_id, to_reserve))

        # Track available stock for each ingredient, decrement as we reserve
        available_cache = {}
        for _, metadata_id, _ in reservation_requests:
            if metadata_id not in available_cache:
                available_physical = IngredientStockDB.get_available_stock(metadata_id)
                reserved_global = ReservationDB.get_reserved_qty(metadata_id)
                available_cache[metadata_id] = max(0, (available_physical or 0) - (reserved_global or 0))

        for lineitem_id, metadata_id, to_reserve in reservation_requests:
            available = available_cache[metadata_id]
            reserve_now = min(to_reserve, available)
            if reserve_now > 0:
                ReservationDB.add_reservation(order_id, lineitem_id, metadata_id, reserve_now)
                available_cache[metadata_id] -= reserve_now

        QtWidgets.QMessageBox.information(self.ui, "Reservation Complete", "Ingredients reserved for this order.")
        self.load_ingredients(order_id)

    def release_reservations(self):
        selected = self.ui.orders_table.currentRow()
        if selected < 0:
            QtWidgets.QMessageBox.warning(self.ui, "No Order Selected", "Please select an order to release reservations for.")
            return
        order_id = int(self.ui.orders_table.item(selected, 0).text())

        # Get all reservations for this order
        reservations = ReservationDB.get_reservations(order_id=order_id, status='active')
        if not reservations:
            QtWidgets.QMessageBox.information(self.ui, "No Reservations", "No active reservations found for this order.")
            return

        for reservation in reservations:
            reservation_id = reservation[0]  # Assuming id is the first column
            ReservationDB.release_reservation(reservation_id)

        QtWidgets.QMessageBox.information(self.ui, "Released", "All reservations for this order have been released.")
        self.load_ingredients(order_id)