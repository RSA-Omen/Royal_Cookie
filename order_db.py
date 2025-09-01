from db import get_connection

class OrderDB:

    @staticmethod
    def recalculate_total_amount(order_id):
        """
        Recalculate and update the total_amount for an order based on its line items and recipe standard price per unit.
        """
        try:
            from line_item_db import LineItemDB
            from recipe_db import RecipeDB
            items = LineItemDB.get_order_items(order_id)
            total = 0.0
            for item in items:
                # item: (lineitem_id, order_id, recipe_name, quantity)
                recipe_id = LineItemDB.get_recipe_id(item[0])
                qty = item[3]
                # Get standard price per unit and output_quantity for this recipe
                recipe = None
                for r in RecipeDB.get_all_recipes():
                    if r[0] == recipe_id:
                        recipe = r
                        break
                if recipe:
                    price_per_unit = recipe[3] if recipe[3] is not None else 10.0
                    output_quantity = recipe[2] if recipe[2] is not None else 1
                    total += price_per_unit * qty * output_quantity
            # Update the order's total_amount
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("UPDATE orders SET total_amount=? WHERE id=?", (total, order_id))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"[ERROR] Failed to recalculate total_amount for order {order_id}: {e}")
    @staticmethod
    def get_orders_by_customer(customer_id):
        """Return all orders for a specific customer, ordered by order_date descending."""
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT id, order_date, status
                FROM orders
                WHERE customer_id = ?
                ORDER BY order_date DESC
            """, (customer_id,))
            rows = cur.fetchall()
            conn.close()
            return rows
        except Exception as e:
            print(f"[ERROR] Failed to fetch orders for customer {customer_id}: {e}")
            return []

    @staticmethod
    def init_orders_table(connection):
        """Create the orders table if it doesn't exist."""
        try:
            cur = connection.cursor()
            cur.execute('''
                CREATE TABLE IF NOT EXISTS orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    customer_id INTEGER NOT NULL,
                    order_date TEXT NOT NULL,
                    delivery_date TEXT,
                    status TEXT NOT NULL,
                    total_amount REAL DEFAULT 0,
                    notes TEXT,
                    FOREIGN KEY(customer_id) REFERENCES customers(id)
                )
            ''')
            connection.commit()
        except Exception as e:
            print(f"[ERROR] Failed to initialize orders table: {e}")

    @staticmethod
    def get_all_orders():
        """Return all orders with customer names."""
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT o.id, c.name, o.status, o.order_date, o.delivery_date, o.total_amount, o.notes
                FROM orders o
                JOIN customers c ON o.customer_id = c.id
                ORDER BY o.order_date DESC
            """)
            rows = cur.fetchall()
            conn.close()
            return rows
        except Exception as e:
            print(f"[ERROR] Failed to fetch all orders: {e}")
            return []

    @staticmethod
    def add_order(customer_id, delivery_date=None, notes="New Order"):
        """
        Insert a new order for the given customer.
        Returns the order_id of the new order.
        """
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO orders (customer_id, order_date, delivery_date, status, total_amount, notes)
                VALUES (?, DATE('now'), ?, 'New Order', 0, ?)
            """, (customer_id, delivery_date, notes))
            conn.commit()
            order_id = cur.lastrowid
            conn.close()
            return order_id
        except Exception as e:
            print(f"[ERROR] Failed to add order: {e}")
            return None

    @staticmethod
    def delete_order(order_id):
        """
        Delete an order by ID.
        """
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("DELETE FROM orders WHERE id=?", (order_id,))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"[ERROR] Failed to delete order: {e}")

    @staticmethod
    def update_order(order_id, status=None, notes=None):
        """
        Update an order's status and/or notes.
        """
        try:
            conn = get_connection()
            cur = conn.cursor()
            if status:
                cur.execute("UPDATE orders SET status=? WHERE id=?", (status, order_id))
            if notes:
                cur.execute("UPDATE orders SET notes=? WHERE id=?", (notes, order_id))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"[ERROR] Failed to update order: {e}")

