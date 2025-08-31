from order_db import OrderDB
from PyQt5 import QtWidgets,QtGui
from line_item_db import LineItemDB
from recipe_db import RecipeDB
from Stock_db import StockDB
from reservation_db import ReservationDB
from metadata_db import MetadataDB
from order_db import OrderDB
from ingredient_db import IngredientDB

class ProductionController:
    def load_shopping_list(self):
        """
        Populate the shopping list table with all orders and ingredients that have required > reserved + available (i.e., need to be purchased).
        This version aggregates shortages per ingredient (metadata_id) across all orders, and lists which orders need them.
        """
        from order_db import OrderDB
        from line_item_db import LineItemDB
        from Stock_db import StockDB
        from ingredient_db import IngredientDB
        from metadata_db import MetadataDB
        from reservation_db import ReservationDB
        table = self.ui.shopping_table
        table.setRowCount(0)
        # metadata_id -> {name, unit, total_required, total_reserved, total_available, orders: set()}
        ingredient_summary = {}
        orders = OrderDB.get_all_orders()
        for order in orders:
            order_id = order[0]
            required = LineItemDB.get_required_ingredients_for_order(order_id)
            for metadata_id, req_qty in required.items():
                meta = [m for m in MetadataDB.get_all_metadata() if m[0] == metadata_id]
                name = meta[0][1] if meta else str(metadata_id)
                unit = meta[0][3] if meta else ""
                if metadata_id not in ingredient_summary:
                    ingredient_summary[metadata_id] = {
                        "name": name,
                        "unit": unit,
                        "total_required": 0,
                        "total_reserved": 0,
                        "orders": set()
                    }
                ingredient_summary[metadata_id]["total_required"] += req_qty
                ingredient_summary[metadata_id]["orders"].add(order_id)
                # Reserved for this order/ingredient
                reserved = ReservationDB.get_reserved_qty_for_order(order_id, metadata_id)
                ingredient_summary[metadata_id]["total_reserved"] += reserved
        # Now, for each metadata_id, get available in stock (all stock, not just for this order)
        for metadata_id in ingredient_summary:
            ingredient_ids = [ing["ID"] for ing in IngredientDB.get_ingredients() if ing["MetadataID"] == metadata_id]
            available = 0
            for iid in ingredient_ids:
                available += StockDB.get_available_stock(iid)
            ingredient_summary[metadata_id]["total_available"] = available
        # Now, build the shopping list: only those with shortage
        shopping_rows = []
        for metadata_id, info in ingredient_summary.items():
            shortage = info["total_required"] - info["total_reserved"] - info["total_available"]
            if shortage > 0:
                orders_str = ", ".join(str(oid) for oid in sorted(info["orders"]))
                shopping_rows.append([
                    info["name"],
                    f"{shortage} {info['unit']}",
                    orders_str,
                    ""
                ])
        # Populate the table
        for row_idx, row_data in enumerate(shopping_rows):
            table.insertRow(row_idx)
            for col_idx, value in enumerate(row_data):
                table.setItem(row_idx, col_idx, QtWidgets.QTableWidgetItem(str(value) if value is not None else ""))
    def load_reservations(self):
        """
        Populate the reservations table with all reservations for the selected order, showing ingredient names.
        If no order is selected, clear the table.
        """
        table = self.ui.reservations_table
        table.setRowCount(0)
        order_id = None
        if self.ui.order_id_field.text():
            try:
                order_id = int(self.ui.order_id_field.text())
            except Exception:
                order_id = None
        if not order_id and hasattr(self.ui, 'order_combo') and self.ui.order_combo.currentIndex() >= 0:
            # Try to get order_id from combo box
            order_id = self.ui.order_combo.itemData(self.ui.order_combo.currentIndex())
        if not order_id:
            return
        from reservation_db import ReservationDB
        from ingredient_db import IngredientDB
        from line_item_db import LineItemDB
        from Stock_db import StockDB
        reservations = []
        # Gather all reservations for all line items in this order
        items = LineItemDB.get_order_items(order_id)
        for item in items:
            lineitem_id = item[0]
            res_list = ReservationDB.get_reservations_for_lineitem(lineitem_id)
            for res in res_list:
                reservations.append(res)
        for row_idx, res in enumerate(reservations):
            stock_id = res.get("IngredientStockID")
            ingredient_name = ""
            stock_row = None
            if stock_id is not None:
                stock_rows = StockDB.get_stock()
                stock_row = next((s for s in stock_rows if s[0] == stock_id), None)
                if stock_row:
                    ingredient_id = stock_row[1]
                    ing = IngredientDB.get_ingredient_by_id(ingredient_id)
                    if ing:
                        ingredient_name = ing["Name"]
            row_data = [
                res.get("ID", ""),
                order_id,
                res.get("LineItemID", res.get("lineitem_id", "")),
                ingredient_name,
                stock_id,
                "",  # Purchase Date (not tracked in stock row, could be added if needed)
                stock_row[6] if stock_row else "",  # Expiry
                res.get("Qty", ""),
                res.get("ReservedUntil", res.get("reserved_until", "")),
            ]
            table.insertRow(row_idx)
            for col_idx, value in enumerate(row_data):
                table.setItem(row_idx, col_idx, QtWidgets.QTableWidgetItem(str(value) if value is not None else ""))
    def __init__(self, ui):
        self.ui = ui
        # Connect UI signals to controller methods
        self.ui.order_combo.currentIndexChanged.connect(self.on_order_selected)
        self.ui.show_closed_toggle.toggled.connect(self.populate_order_combo)
        self.ui.reserve_btn.clicked.connect(self.on_reserve_ingredients_clicked)
        self.ui.release_btn.clicked.connect(self.release_reservations)
        # self.ui.status_btn.clicked.connect(self.change_order_status)  # Disabled: method not implemented
        # self.ui.notes_text.focusOutEvent = self.save_production_note_on_focus_out  # Disabled: method not implemented
        self.ui.tabs.currentChanged.connect(self._on_tab_changed)
        self.populate_order_combo()

    def on_reserve_ingredients_clicked(self):
        """
        Handler for the Reserve Ingredients button. Iterates over the ingredient summary table and reserves ingredients as needed.
        """
        order_id = int(self.ui.order_id_field.text()) if self.ui.order_id_field.text() else None
        if not order_id:
            print("[ERROR] No order selected.")
            return
        table = self.ui.ingredients_for_lineitem_table
        for row in range(table.rowCount()):
            # Get ingredient name from column 0, required from column 1, available from column 2
            name = table.item(row, 0).text()
            required_str = table.item(row, 1).text().split()[0]
            available_str = table.item(row, 2).text().split()[0]
            try:
                required = float(required_str)
                available = float(available_str)
            except Exception:
                continue
            # Find metadata_id by name (could be optimized if table stores metadata_id as data)
            meta_id = None
            for m in MetadataDB.get_all_metadata():
                if m[1] == name:
                    meta_id = m[0]
                    break
            if meta_id is None:
                print(f"[WARN] Could not find metadata_id for ingredient '{name}'")
                continue
            if available == 0:
                continue
            self.reserve_ingredient(order_id, meta_id, required)
        # Refresh table after all reservations
        self.load_ingredients_for_order(order_id)

        # After reservation, check if all required ingredients are fully reserved
        from PyQt5.QtWidgets import QMessageBox
        reserved_ingredients = []
        for row in range(table.rowCount()):
            name = table.item(row, 0).text()
            required_str = table.item(row, 1).text().split()[0]
            reserved_str = table.item(row, 3).text().split()[0]
            try:
                required = float(required_str)
                reserved = float(reserved_str)
            except Exception:
                continue
            if required > 0 and reserved >= required:
                reserved_ingredients.append(name)
        if reserved_ingredients:
            msg = QMessageBox(self.ui)
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle("Reservation Complete")
            msg.setText("The following ingredients have been reserved as much as possible:")
            msg.setInformativeText("\n".join(reserved_ingredients))
            msg.exec_()
    def reserve_ingredient(self, order_id, metadata_id, required_qty):
        """
        Reserve the required quantity of an ingredient for an order, per line item (recipe).
        After each reservation, recalculate reserved and available, and skip further reservations if enough is already reserved.
        """
        import datetime
        now = datetime.datetime.now().isoformat(sep=' ', timespec='seconds')
        # Get all line items in the order that require this ingredient
        items = LineItemDB.get_order_items(order_id)
        for item in items:
            lineitem_id = item[0]
            quantity = item[3]
            recipe_id = LineItemDB.get_recipe_id(lineitem_id)
            if not recipe_id:
                continue
            # Find how much of this ingredient is needed for this line item
            needed = 0
            for ing in RecipeDB.get_recipe_ingredients(recipe_id):
                if ing[2] == metadata_id:
                    needed = ing[3] * quantity
                    break
            if needed == 0:
                continue
            # Check how much is already reserved for this ingredient in this order
            total_reserved = ReservationDB.get_reserved_qty_for_order(order_id, metadata_id)
            if total_reserved >= required_qty:
                # Already reserved enough for the whole order, skip further reservations
                break
            # Reserve from stock batches (FIFO)
            stock_batches = [s for s in StockDB.get_stock() if IngredientDB.get_ingredient_by_id(s[1]) and IngredientDB.get_ingredient_by_id(s[1])["MetadataID"] == metadata_id and s[3] > 0]
            stock_batches.sort(key=lambda s: (s[6] if s[6] else '', s[0]))
            to_reserve = min(needed, required_qty - total_reserved)
            for batch in stock_batches:
                stock_id = batch[0]
                available = batch[3]
                if available == 0:
                    continue
                reserve_qty = min(available, to_reserve)
                status = "ready" if reserve_qty == to_reserve else "partial"
                ReservationDB.add_reservation(
                    lineitem_id=lineitem_id,
                    ingredient_stock_id=stock_id,
                    qty=reserve_qty,
                    status=status,
                    reserved_until=None
                )
                StockDB.update_stock(stock_id, available - reserve_qty)
                to_reserve -= reserve_qty
                # Recalculate total_reserved after each reservation
                total_reserved = ReservationDB.get_reserved_qty_for_order(order_id, metadata_id)
                if total_reserved >= required_qty or to_reserve <= 0:
                    break
            # If after this line item, enough is reserved, stop
            if total_reserved >= required_qty:
                break
        # After all, update the table
        self.load_ingredients_for_order(order_id)


    def populate_order_combo(self):
        """Populate the order combobox based on the toggle state and select the first order by default."""
        show_closed = self.ui.show_closed_toggle.isChecked()
        self.ui.order_combo.blockSignals(True)
        self.ui.order_combo.clear()

        self._orders = OrderDB.get_all_orders()
        for order in self._orders:
            # order: (id, customer_name, status, order_date, delivery_date, total_amount, notes)
            if not show_closed and order[2].lower() == "closed":
                continue
            display = f"{order[0]} - {order[1]} ({order[2]})"
            self.ui.order_combo.addItem(display, order[0])
        self.ui.order_combo.blockSignals(False)
        # Auto-select first order if available and populate fields
        if self.ui.order_combo.count() > 0:
            self.ui.order_combo.setCurrentIndex(0)
            self.on_order_selected(0)
        else:
            self.clear_order_fields()

    def on_order_selected(self, idx):
        if idx < 0 or not hasattr(self, '_orders') or self.ui.order_combo.count() == 0:
            self.clear_order_fields()
            self.ui.lineitems_table.setRowCount(0)
            return
        order_id = self.ui.order_combo.itemData(idx)
        # Find the order tuple by id
        order = next((o for o in self._orders if o[0] == order_id), None)
        if not order:
            self.clear_order_fields()
            self.ui.lineitems_table.setRowCount(0)
            return
        # order: (id, customer_name, status, order_date, delivery_date, total_amount, notes)
        self.ui.order_id_field.setText(str(order[0]))
        self.ui.customer_field.setText(order[1])
        self.ui.status_field.setText(order[2])
        self.ui.delivery_date_field.setText(order[4] or "")
        self.ui.total_field.setText(str(order[5]))
        self.ui.notes_field.setText(order[6] or "")
        self.load_line_items(order_id)

    def clear_order_fields(self):
        self.ui.order_id_field.clear()
        self.ui.customer_field.clear()
        self.ui.status_field.clear()
        self.ui.delivery_date_field.clear()
        self.ui.total_field.clear()
        self.ui.notes_field.clear()

    def load_inventory(self):
        """Populate the inventory table with all stock batches from StockDB, showing ingredient name."""

        table = self.ui.inventory_table
        table.setRowCount(0)
        stock_rows = StockDB.get_stock()
        # stock: (id, ingredient_id, purchase_id, quantity, last_updated, batch_number, expiry_date)
        table.setColumnCount(7)
        table.setHorizontalHeaderLabels([
            "Stock ID", "Ingredient Name", "Purchase ID", "Quantity", "Last Updated", "Batch Number", "Expiry Date"
        ])
        for row_idx, stock in enumerate(stock_rows):
            ingredient = IngredientDB.get_ingredient_by_id(stock[1])
            ingredient_name = ingredient["Name"] if ingredient and "Name" in ingredient else str(stock[1])
            row_data = [stock[0], ingredient_name, stock[2], stock[3], stock[4], stock[5], stock[6]]
            table.insertRow(row_idx)
            for col_idx, value in enumerate(row_data):
                table.setItem(row_idx, col_idx, QtWidgets.QTableWidgetItem(str(value) if value is not None else ""))

    def load_line_items(self, order_id):
        """Populate the line items table for the selected order."""
        table = self.ui.lineitems_table
        table.setRowCount(0)
        items = LineItemDB.get_order_items(order_id)
        for row_idx, item in enumerate(items):
            # item: (lineitem_id, order_id, recipe_name, quantity, reserved_qty, status, notes)
            table.insertRow(row_idx)
            table.setItem(row_idx, 0, QtWidgets.QTableWidgetItem(str(item[2])))  # Recipe Name
            table.setItem(row_idx, 1, QtWidgets.QTableWidgetItem(str(item[3])))  # Quantity
            table.setItem(row_idx, 2, QtWidgets.QTableWidgetItem(str(item[4]) if len(item) > 4 else ""))  # Reserved Qty
            table.setItem(row_idx, 3, QtWidgets.QTableWidgetItem(str(item[5]) if len(item) > 5 else ""))  # Status
            table.setItem(row_idx, 4, QtWidgets.QTableWidgetItem(str(item[6]) if len(item) > 6 else ""))  # Notes
        # After loading line items, load the ingredient summary for the order
        self.load_ingredients_for_order(order_id)

    def on_lineitem_selected(self, row, _column):
        # No longer used for summary table; could be used for per-lineitem drilldown if needed
        pass

    def load_ingredients_for_order(self, order_id):
        """Summarize all ingredients needed for the order, show quantity+unit, available+unit, reserved+unit."""

        table = self.ui.ingredients_for_lineitem_table
        table.setRowCount(0)
        items = LineItemDB.get_order_items(order_id)
        # Aggregate required quantities by metadata_id
        ingredient_summary = {}  # metadata_id: {name, unit, required}
        for item in items:
            lineitem_id, order_id, recipe_name, quantity, *_ = item
            recipe_id = LineItemDB.get_recipe_id(lineitem_id)
            if not recipe_id:
                continue
            ingredients = RecipeDB.get_recipe_ingredients(recipe_id)
            for ing in ingredients:
                metadata_id = ing[2]
                name = ing[5]
                per_recipe_amt = ing[3]
                # Get unit from metadata
                unit = ""
                meta = [m for m in MetadataDB.get_all_metadata() if m[0] == metadata_id]
                if meta:
                    unit = meta[0][3]
                required = per_recipe_amt * quantity
                if metadata_id not in ingredient_summary:
                    ingredient_summary[metadata_id] = {"name": name, "unit": unit, "required": 0}
                ingredient_summary[metadata_id]["required"] += required
        
        # Now, for each metadata_id, get available and reserved
        for idx, (metadata_id, info) in enumerate(ingredient_summary.items()):
            name = info["name"]
            unit = info["unit"]
            required = info["required"]
            # Available: sum all stock for this metadata
            available = 0
            all_stock = StockDB.get_stock()
            for stock in all_stock:
                # stock: (id, ingredient_id, purchase_id, quantity, last_updated, batch_number, expiry_date)
                ingredient_id = stock[1]
                # Get ingredient's metadata_id

                ing = IngredientDB.get_ingredient_by_id(ingredient_id)
                if ing and ing["MetadataID"] == metadata_id:
                    available += stock[3]
            # Reserved: for this order and this metadata
            reserved = 0
            reserved = ReservationDB.get_reserved_qty_for_order(order_id, metadata_id)
            # Populate table
            table.insertRow(idx)
            table.setItem(idx, 0, QtWidgets.QTableWidgetItem(str(name)))
            table.setItem(idx, 1, QtWidgets.QTableWidgetItem(f"{required} {unit}"))
            table.setItem(idx, 2, QtWidgets.QTableWidgetItem(f"{available} {unit}"))
            table.setItem(idx, 3, QtWidgets.QTableWidgetItem(f"{reserved} {unit}"))

    def release_reservations(self):
        """
        For the selected order, move all reservations back to stock and remove the reservations.
        Update line item statuses to not ready.
        """
        print("releasing")

        order_id = int(self.ui.order_id_field.text()) if self.ui.order_id_field.text() else None
        if not order_id:
            return
        # For each line item, restore stock and delete reservations
        items = LineItemDB.get_order_items(order_id)
        for item in items:
            lineitem_id = item[0]
            # Get all reservations for this lineitem
            reservations = ReservationDB.get_reservations_for_lineitem(lineitem_id)
            for res in reservations:
                stock_id = res.get("IngredientStockID")
                qty = res.get("Qty", 0)
                if stock_id is not None:
                    # Increase stock by released qty
                    stock = StockDB.get_stock()
                    for s in stock:
                        if s[0] == stock_id:
                            StockDB.update_stock(stock_id, s[3] + qty)
                            break
                # Delete reservation
                ReservationDB.delete_reservation(res["ID"])
            # No lineitem status update needed; status is tracked via reservations
        # Refresh ingredient summary and inventory tables
        self.load_ingredients_for_order(order_id)
        self.load_inventory()

    def _on_tab_changed(self, idx):
        tab_name = self.ui.tabs.tabText(idx)
        if tab_name == "Reservations":
            self.load_reservations()
        elif tab_name == "Inventory":
            self.load_inventory()
        elif tab_name == "Shopping List":
            self.load_shopping_list()