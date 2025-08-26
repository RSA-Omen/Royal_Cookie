from db import get_connection

class LineItemDB:

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
            connection.close()
        except Exception as e:
            print(f"[ERROR] Failed to initialize line_items table: {e}")



    @staticmethod
    def get_order_items(order_id):
        """
        Fetch all line items for a given order.
        Returns a list of tuples: (id, order_id, recipe_id, quantity)
        """
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT li.id, li.order_id, r.name, li.quantity
                FROM line_items li
                JOIN recipes r ON li.recipe_id = r.id
                WHERE li.order_id=?
            """, (order_id,))
            rows = cur.fetchall()
            conn.close()
            return rows
        except Exception as e:
            print(f"[ERROR] Failed to fetch order items: {e}")
            return []

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
