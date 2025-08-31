from db import get_connection

class LineItemDB:

    @staticmethod
    def get_required_ingredients_for_order(order_id):
        """
        Aggregate required quantity for each ingredient (metadata_id) for the given order.
        Returns a dict: {metadata_id: required_qty}
        """
        from recipe_db import RecipeDB
        required = {}
        items = LineItemDB.get_order_items(order_id)
        for item in items:
            lineitem_id = item[0]
            quantity = item[3]
            recipe_id = LineItemDB.get_recipe_id(lineitem_id)
            if not recipe_id:
                continue
            ingredients = RecipeDB.get_recipe_ingredients(recipe_id)
            for ing in ingredients:
                metadata_id = ing[2]
                per_recipe_amt = ing[3]
                total_needed = per_recipe_amt * quantity
                if metadata_id not in required:
                    required[metadata_id] = 0
                required[metadata_id] += total_needed
        return required

    @staticmethod
    def get_reservation_status_for_order(order_id):
        """
        For each required ingredient in the order, return required, reserved, and ready status.
        Returns a dict: {metadata_id: {"required": x, "reserved": y, "ready": bool}}
        """
        from reservation_db import ReservationDB
        required = LineItemDB.get_required_ingredients_for_order(order_id)
        status = {}
        for metadata_id, req_qty in required.items():
            reserved_qty = ReservationDB.get_reserved_qty_for_order(order_id, metadata_id)
            status[metadata_id] = {
                "required": req_qty,
                "reserved": reserved_qty,
                "ready": reserved_qty >= req_qty
            }
        return status

    @staticmethod

    def init_line_items_table(connection):
        try:
            cur = connection.cursor()
            cur.execute('''
                CREATE TABLE IF NOT EXISTS line_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_id INTEGER NOT NULL,
                    recipe_id INTEGER NOT NULL,
                    quantity INTEGER NOT NULL,
                    FOREIGN KEY(order_id) REFERENCES orders(id),
                    FOREIGN KEY(recipe_id) REFERENCES recipes(id)
                )
            ''')
            connection.commit()
        except Exception as e:
            print(f"[ERROR] Failed to initialize line_items table: {e}")



    @staticmethod
    def get_order_items(order_id):
        """
        Fetch all line items for a specific order.
        Returns a list of tuples:
        (lineitem_id, order_id, recipe_name, quantity, unit)
        """
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("""
                        SELECT li.id, li.order_id, r.name, li.quantity
                        FROM line_items li
                                 JOIN recipes r ON li.recipe_id = r.id
                        WHERE li.order_id = ?
                        """, (order_id,))
            items = cur.fetchall()
            conn.close()
            return items
        except Exception as e:
            print(f"[ERROR] Failed to fetch order items: {e}")
            return []

    @staticmethod
    def get_recipe_id(lineitem_id):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT recipe_id FROM line_items WHERE id=?", (lineitem_id,))
        row = cur.fetchone()
        conn.close()
        return row[0] if row else None

    @staticmethod
    def add_order_item(order_id, recipe_id, quantity):
        """Add a new line item to an order."""
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO line_items (order_id, recipe_id, quantity)
                VALUES (?, ?, ?)
            """, (order_id, recipe_id, quantity))
            conn.commit()
            lineitem_id = cur.lastrowid
            conn.close()
            return lineitem_id
        except Exception as e:
            print(f"[ERROR] Failed to add order item: {e}")
            return None

    @staticmethod
    def update_order_item(lineitem_id, new_qty):
        """Update the quantity of a line item by its ID."""
        if new_qty <= 0:
            raise ValueError("Quantity must be greater than zero.")
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute(
                "UPDATE line_items SET quantity=? WHERE id=?",
                (new_qty, lineitem_id)
            )
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"[ERROR] Failed to update line item: {e}")
            return False

    @staticmethod
    def delete_order_item(lineitem_id):
        """Delete a line item by its ID."""
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("DELETE FROM line_items WHERE id=?", (lineitem_id,))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"[ERROR] Failed to delete order item: {e}")

    @staticmethod
    def get_all_recipes():
        """Return a list of all recipes: (id, name)"""
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("SELECT id, name FROM recipes ORDER BY name")
            rows = cur.fetchall()
            conn.close()
            return rows
        except Exception as e:
            print(f"[ERROR] Failed to fetch recipes: {e}")
            return []
    
