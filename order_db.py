from db import get_connection

class OrderDB:
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
