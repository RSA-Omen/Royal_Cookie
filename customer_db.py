from db import get_connection
from datetime import datetime

class CustomerDB:
    @staticmethod
    def get_all_customers():
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM customer")
        rows = cur.fetchall()
        conn.close()
        return [{"ID": r[0], "Name": r[1], "Phone": r[2], "Email": r[3]} for r in rows]

    @staticmethod
    def init_customer_db(conn):
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT,
                email TEXT,
                subscribed INTEGER DEFAULT 0,
                address TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                notes TEXT
            )
        ''')
        conn.commit()

    @staticmethod
    def add_customer(name, phone=None, email=None, subscribed=0, address=None, notes=None):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute('''
            INSERT INTO customers (name, phone, email, subscribed, address, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (name, phone, email, subscribed, address, notes))
        conn.commit()
        cid = cur.lastrowid
        conn.close()
        return cid

    @staticmethod
    def get_customers():
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM customers")
        rows = cur.fetchall()
        conn.close()
        return rows

    @staticmethod
    def update_customer(cid, name=None, phone=None, email=None, subscribed=None, address=None, notes=None):
        conn = get_connection()
        cur = conn.cursor()
        # Build update dynamically
        fields = []
        values = []
        if name is not None: fields.append("name=?"); values.append(name)
        if phone is not None: fields.append("phone=?"); values.append(phone)
        if email is not None: fields.append("email=?"); values.append(email)
        if subscribed is not None: fields.append("subscribed=?"); values.append(subscribed)
        if address is not None: fields.append("address=?"); values.append(address)
        if notes is not None: fields.append("notes=?"); values.append(notes)
        values.append(cid)
        cur.execute(f"UPDATE customers SET {', '.join(fields)} WHERE id=?", values)
        conn.commit()
        conn.close()

    @staticmethod
    def delete_customer(cid):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM customers WHERE id=?", (cid,))
        conn.commit()
        conn.close()
