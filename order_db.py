from db import get_connection

class OrderDB:

    @staticmethod
    def init_orders_table(connection):
        """Create the orders table if it doesn't exist."""
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute('''
                CREATE TABLE IF NOT EXISTS orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    customer_id INTEGER NOT NULL,
                    order_date TEXT NOT NULL,
                    status TEXT NOT NULL,
                    total_amount REAL DEFAULT 0,
                    notes TEXT,
                    FOREIGN KEY(customer_id) REFERENCES customers(id)
                )
            ''')
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"[ERROR] Failed to initialize orders table: {e}")

    @staticmethod
    def get_orders_by_customer(customer_id):
        """
        Fetch all orders belonging to a specific customer.
        Returns a list of tuples (id, order_date, status, total_amount, notes).
        """
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT id, order_date, status, total_amount, notes
                FROM orders
                WHERE customer_id=?
            """, (customer_id,))
            rows = cur.fetchall()
            conn.close()
            return rows
        except Exception as e:
            print(f"[ERROR] Failed to fetch orders: {e}")
            return []

    @staticmethod
    def add_order(customer_id, notes="New Order"):
        """
        Insert a new order for the given customer.
        Returns the order_id of the new order.
        """
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO orders (customer_id, order_date, status, total_amount, notes)
                VALUES (?, DATE('now'), 'New Order', 0, ?)
            """, (customer_id, notes))
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

    @staticmethod
    def get_all_recipes():
        """
        Fetch all recipes.
        Returns a list of tuples (id, name).
        """
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("SELECT id, name FROM recipes")
            recipes = cur.fetchall()
            conn.close()
            return recipes
        except Exception as e:
            print(f"[ERROR] Failed to fetch recipes: {e}")
            return []

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

    def get_all_orders():
        """Return all orders in the database."""
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT id, customer_id, order_date, status, total_amount, notes
                FROM orders
                ORDER BY order_date DESC
            """)
            rows = cur.fetchall()
            conn.close()
            return rows
        except Exception as e:
            print(f"[ERROR] Failed to fetch all orders: {e}")
            return []