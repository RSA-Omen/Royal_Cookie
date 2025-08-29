from order_db import OrderDB
from PyQt5 import QtWidgets,QtGui
from line_item_db import LineItemDB
from recipe_db import RecipeDB
from Stock_db import StockDB
from reservation_db import ReservationDB


class ProductionController:
    def load_inventory(self):
        """Populate the inventory table with current stock, batch, expiry, reserved, and available quantities."""
        table = self.ui.inventory_table
        from ingredient_db import IngredientDB
        from Stock_db import IngredientStockDB
        from reservation_db import ReservationDB
        # Get all ingredients (metadata)
        ingredients = IngredientDB.get_all_ingredients()
        # Get all stock records
        stock_records = IngredientStockDB.get_stock()
        # Build a map: ingredient_id -> total reserved
        reserved_map = {}
        for ing in ingredients:
            metadata_id = ing["MetadataID"]
            reserved_map[metadata_id] = ReservationDB.get_reserved_qty(metadata_id)
        table.setRowCount(0)
        for stock in stock_records:
            # stock: (id, ingredient_id, quantity, last_updated)
            stock_id, ingredient_id, quantity, last_updated = stock
            # Find ingredient info
            ing = next((i for i in ingredients if i["ID"] == ingredient_id), None)
            if not ing:
                continue
            name = ing["Name"]
            unit = ing["Unit"]
            # Reserved for this ingredient
            reserved = reserved_map.get(ingredient_id, 0)
            available = max(0, quantity - reserved)
            # For now, batch = stock_id, purchase date = last_updated, expiry = ""
            row_idx = table.rowCount()
            table.insertRow(row_idx)
            table.setItem(row_idx, 0, QtWidgets.QTableWidgetItem(str(name)))
            table.setItem(row_idx, 1, QtWidgets.QTableWidgetItem(str(stock_id)))
            table.setItem(row_idx, 2, QtWidgets.QTableWidgetItem(str(last_updated)))
            table.setItem(row_idx, 3, QtWidgets.QTableWidgetItem(""))
            table.setItem(row_idx, 4, QtWidgets.QTableWidgetItem(f"{available} {unit}"))
            table.setItem(row_idx, 5, QtWidgets.QTableWidgetItem(f"{reserved} {unit}"))
    def load_reservations(self):
        """Load all active reservations and display in the reservations table."""
        table = self.ui.reservations_table
        from reservation_db import ReservationDB
        from order_db import OrderDB
        from line_item_db import LineItemDB
        from metadata_db import MetadataDB
        from ingredient_db import IngredientDB
        from purchases_db import PurchaseDB
        reservations = ReservationDB.get_reservations(status='active')
        table.setRowCount(0)
        for row_idx, res in enumerate(reservations):
            # reservations: id, order_id, lineitem_id, metadata_id, qty, reserved_at, reserved_until, status
            res_id, order_id, lineitem_id, metadata_id, qty, reserved_at, reserved_until, status = res
            # Get order info
            order = None
            try:
                order = OrderDB.get_all_orders()
                order = next((o for o in order if o[0] == order_id), None)
            except Exception:
                pass
            # Get line item info
            lineitem = None
            try:
                lineitem = LineItemDB.get_order_items(order_id)
                lineitem = next((li for li in lineitem if li[0] == lineitem_id), None)
            except Exception:
                pass
            # Get ingredient info
            ingredient = None
            try:
                ingredient = MetadataDB.get_all_metadata()
                ingredient = next((m for m in ingredient if m[0] == metadata_id), None)
            except Exception:
                pass
            # Get batch/purchase info (optional, may be blank)
            batch = ""
            purchase_date = ""
            expiry = ""
            # (You can expand this if you track batch/expiry per reservation)
            # Compose display values
            table.insertRow(row_idx)
            table.setItem(row_idx, 0, QtWidgets.QTableWidgetItem(str(res_id)))
            table.setItem(row_idx, 1, QtWidgets.QTableWidgetItem(str(order_id)))
            table.setItem(row_idx, 2, QtWidgets.QTableWidgetItem(str(lineitem_id)))
            table.setItem(row_idx, 3, QtWidgets.QTableWidgetItem(ingredient[1] if ingredient else str(metadata_id)))
            table.setItem(row_idx, 4, QtWidgets.QTableWidgetItem(batch))
            table.setItem(row_idx, 5, QtWidgets.QTableWidgetItem(purchase_date))
            table.setItem(row_idx, 6, QtWidgets.QTableWidgetItem(expiry))
            table.setItem(row_idx, 7, QtWidgets.QTableWidgetItem(str(qty)))
            table.setItem(row_idx, 8, QtWidgets.QTableWidgetItem(str(reserved_until or "")))

    def __init__(self, ui):
        print("ProductionController initialized")
        self.ui = ui
        self.load_orders()
        self.ui.orders_table.itemSelectionChanged.connect(self.on_order_selected)
        self.ui.reserve_btn.clicked.connect(self.reserve_ingredients)
        self.ui.release_btn.clicked.connect(self.release_reservations)
        self.ui.status_btn.clicked.connect(self.change_order_status)
        self.ui.notes_text.focusOutEvent = self.save_production_note_on_focus_out

        # Load reservations and inventory tabs on startup
        self.load_reservations()
        self.load_inventory()
        self.ui.tabs.currentChanged.connect(self._on_tab_changed)

    def _on_tab_changed(self, idx):
        # Reload reservations or inventory when switching to the tab
        tab_text = self.ui.tabs.tabText(idx)
        if tab_text == "Reservations":
            self.load_reservations()
        elif tab_text == "Inventory":
            self.load_inventory()

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
        # If Reservations tab is active, release selected reservations
        if self.ui.tabs.tabText(self.ui.tabs.currentIndex()) == "Reservations":
            selected_rows = self.ui.reservations_table.selectionModel().selectedRows()
            if not selected_rows:
                QtWidgets.QMessageBox.warning(self.ui, "No Selection", "Please select one or more reservations to release.")
                return
            # Collect unique order_ids from selected reservation rows
            order_ids = set()
            for idx in selected_rows:
                order_id_item = self.ui.reservations_table.item(idx.row(), 1)
                if order_id_item:
                    order_ids.add(int(order_id_item.text()))
            if not order_ids:
                QtWidgets.QMessageBox.warning(self.ui, "No Order Found", "Could not determine order(s) from selection.")
                return
            released_any = False
            for order_id in order_ids:
                reservations = ReservationDB.get_reservations(order_id=order_id, status='active')
                for reservation in reservations:
                    reservation_id = reservation[0]
                    ReservationDB.release_reservation(reservation_id)
                    released_any = True
            if released_any:
                QtWidgets.QMessageBox.information(self.ui, "Released", "All reservations for the selected order(s) have been released.")
            else:
                QtWidgets.QMessageBox.information(self.ui, "No Reservations", "No active reservations found for the selected order(s).")
            self.load_reservations()
            return
        else:
            # Default: release all reservations for selected order
            selected = self.ui.orders_table.currentRow()
            if selected < 0:
                QtWidgets.QMessageBox.warning(self.ui, "No Order Selected", "Please select an order to release reservations for.")
                return
            order_id = int(self.ui.orders_table.item(selected, 0).text())
            reservations = ReservationDB.get_reservations(order_id=order_id, status='active')
            if not reservations:
                QtWidgets.QMessageBox.information(self.ui, "No Reservations", "No active reservations found for this order.")
                return
            for reservation in reservations:
                reservation_id = reservation[0]  # Assuming id is the first column
                ReservationDB.release_reservation(reservation_id)
            QtWidgets.QMessageBox.information(self.ui, "Released", "All reservations for this order have been released.")
            self.load_ingredients(order_id)




    def load_ingredients(self, order_id):
        """
        Populate the Required Ingredients table for the selected order,
        showing the total required, reserved, available, and shortage for each ingredient.
        Reserved and Batch/Expiry are left blank for now.
        """
        table = self.ui.ingredients_table
        table.setRowCount(0)
        items = LineItemDB.get_order_items(order_id)
        ingredient_totals = {}  # key: (ingredient_id, ing_name, unit), value: total required

        from ingredient_db import IngredientDB

        for item in items:
            lineitem_id, order_id, recipe_name, quantity = item
            recipe_id = LineItemDB.get_recipe_id(lineitem_id)
            if not recipe_id:
                continue
            ingredients = RecipeDB.get_recipe_ingredients(recipe_id)
            for ing in ingredients:
                # ing: (ri_id, r_id, metadata_id, per_recipe_amt, unit, ing_name, ingredient_id)
                # Make sure your get_recipe_ingredients returns ingredient_id as the last element!
                if len(ing) >= 7:
                    ingredient_id = ing[6]
                else:
                    ingredient_id = ing[2]  # fallback, but not ideal
                ing_name = ing[5]
                per_recipe_amt = ing[3]
                # Fetch the correct unit from ingredient table
                ingredient = IngredientDB.get_ingredient_by_id(ingredient_id)
                unit = ingredient["Unit"] if ingredient and "Unit" in ingredient else ing[4]
                required = per_recipe_amt * quantity

                key = (ingredient_id, ing_name, unit)
                if key not in ingredient_totals:
                    ingredient_totals[key] = 0
                ingredient_totals[key] += required

        stock_db = IngredientStockDB()

        for row_idx, ((ingredient_id, ing_name, unit), total_required) in enumerate(ingredient_totals.items()):
            reserved = ReservationDB.get_reserved_qty_for_order(order_id, ingredient_id)
            available_physical = stock_db.get_available_stock(ingredient_id)
            reserved_global = ReservationDB.get_reserved_qty(ingredient_id)
            available = max(0, (available_physical or 0) - (reserved_global or 0))
            shortage = max(0, total_required - (available - reserved))

            table.insertRow(row_idx)
            table.setItem(row_idx, 0, QtWidgets.QTableWidgetItem(str(ing_name)))
            table.setItem(row_idx, 1, QtWidgets.QTableWidgetItem(f"{total_required} {unit}"))
            table.setItem(row_idx, 2, QtWidgets.QTableWidgetItem(f"{reserved} {unit}"))
            table.setItem(row_idx, 3, QtWidgets.QTableWidgetItem(f"{available} {unit}"))
            table.setItem(row_idx, 4, QtWidgets.QTableWidgetItem(f"{shortage} {unit}"))
            table.setItem(row_idx, 5, QtWidgets.QTableWidgetItem(""))

            # Coloring logic
            if reserved >= total_required:
                color = QtGui.QColor(144, 238, 144)  # green: fully reserved
            elif reserved > 0 and shortage == 0:
                color = QtGui.QColor(255, 255, 102)  # yellow: partially reserved, but enough available
            else:
                color = QtGui.QColor(255, 99, 71)    # red: not enough reserved and not enough available

            for col in range(table.columnCount()):
                cell_item = table.item(row_idx, col)
                if cell_item is not None:
                    cell_item.setBackground(color)