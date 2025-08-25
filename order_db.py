from db import get_connection
from datetime import datetime

class OrderDB:
    @staticmethod
    def init_order_db(conn):
        cur = conn.cursor()
        # Orders table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER NOT NULL,
                order_date TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'pending',
                total_amount REAL DEFAULT 0,
                notes TEXT,
                FOREIGN KEY(customer_id) REFERENCES customers(id)
            )
        """)
        # Order items table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS order_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL,
                recipe_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                price REAL DEFAULT 0,
                FOREIGN KEY(order_id) REFERENCES orders(id) ON DELETE CASCADE,
                FOREIGN KEY(recipe_id) REFERENCES recipes(id)
            )
        """)
        conn.commit()

    # ------------------ Orders Methods ------------------
    @staticmethod
    def get_all_orders():
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT o.id, o.customer_id, c.name, o.order_date, o.notes
            FROM orders o
            JOIN customer c ON o.customer_id = c.id
        """)
        rows = cur.fetchall()
        conn.close()
        return [
            {"ID": r[0], "customer_id": r[1], "CustomerName": r[2], "OrderDate": r[3], "Notes": r[4]}
            for r in rows
        ]


    @staticmethod
    def add_order(customer_id, notes=None):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO orders (customer_id, notes) VALUES (?, ?)",
            (customer_id, notes)
        )
        conn.commit()
        order_id = cur.lastrowid
        conn.close()
        return order_id

    @staticmethod
    def get_orders():
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM orders")
        rows = cur.fetchall()
        conn.close()
        return rows

    @staticmethod
    def update_order(order_id, status=None, total_amount=None, notes=None):
        conn = get_connection()
        cur = conn.cursor()
        query = "UPDATE orders SET "
        updates = []
        params = []
        if status is not None:
            updates.append("status=?")
            params.append(status)
        if total_amount is not None:
            updates.append("total_amount=?")
            params.append(total_amount)
        if notes is not None:
            updates.append("notes=?")
            params.append(notes)
        query += ", ".join(updates) + " WHERE id=?"
        params.append(order_id)
        cur.execute(query, tuple(params))
        conn.commit()
        conn.close()

    @staticmethod
    def delete_order(order_id):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM orders WHERE id=?", (order_id,))
        conn.commit()
        conn.close()

    # ------------------ Order Items Methods ------------------
    @staticmethod
    def add_order_item(order_id, recipe_id, quantity, price=0):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO order_items (order_id, recipe_id, quantity, price) VALUES (?, ?, ?, ?)",
            (order_id, recipe_id, quantity, price)
        )
        conn.commit()
        conn.close()

    @staticmethod
    def get_order_items(order_id):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM order_items WHERE order_id=?", (order_id,))
        rows = cur.fetchall()
        conn.close()
        return rows

    @staticmethod
    def update_order_item(item_id, quantity=None, price=None):
        conn = get_connection()
        cur = conn.cursor()
        updates = []
        params = []
        if quantity is not None:
            updates.append("quantity=?")
            params.append(quantity)
        if price is not None:
            updates.append("price=?")
            params.append(price)
        query = "UPDATE order_items SET " + ", ".join(updates) + " WHERE id=?"
        params.append(item_id)
        cur.execute(query, tuple(params))
        conn.commit()
        conn.close()

    @staticmethod
    def delete_order_item(item_id):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM order_items WHERE id=?", (item_id,))
        conn.commit()
        conn.close()
