from db import get_connection
from datetime import datetime

class StockDB:
    @staticmethod
    def init_stock_db(conn):
        """
        Initialize the stock table with purchase_id for batch traceability,
        and optional batch/expiry fields.
        """
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stock (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ingredient_id INTEGER NOT NULL,
                purchase_id INTEGER,
                quantity REAL NOT NULL,
                last_updated TEXT DEFAULT CURRENT_TIMESTAMP,
                batch_number TEXT,           -- Optional
                expiry_date TEXT,            -- Optional
                FOREIGN KEY (ingredient_id) REFERENCES ingredients(id),
                FOREIGN KEY (purchase_id) REFERENCES ingredient_purchases(id)
            )
        ''')
        conn.commit()

    @staticmethod
    def get_stock(ingredient_id=None):
        conn = get_connection()
        cur = conn.cursor()
        if ingredient_id:
            cur.execute("SELECT * FROM stock WHERE ingredient_id = ?", (ingredient_id,))
        else:
            cur.execute("SELECT * FROM stock")
        rows = cur.fetchall()
        conn.close()
        return rows

    @staticmethod
    def add_stock(ingredient_id, quantity, purchase_id=None, batch_number=None, expiry_date=None):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO stock (ingredient_id, quantity, purchase_id, batch_number, expiry_date, last_updated) VALUES (?, ?, ?, ?, ?, ?)",
            (ingredient_id, quantity, purchase_id, batch_number, expiry_date, datetime.now().isoformat())
        )
        conn.commit()
        conn.close()

    @staticmethod
    def get_available_stock(ingredient_id):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT SUM(quantity) FROM stock WHERE ingredient_id=?", (ingredient_id,))
        row = cur.fetchone()
        conn.close()
        return row[0] if row and row[0] is not None else 0

    @staticmethod
    def update_stock(stock_id, quantity, batch_number=None, expiry_date=None):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "UPDATE stock SET quantity=?, last_updated=?, batch_number=?, expiry_date=? WHERE id=?",
            (quantity, datetime.now().isoformat(), batch_number, expiry_date, stock_id)
        )
        conn.commit()
        conn.close()

    @staticmethod
    def delete_stock(stock_id):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM stock WHERE id=?", (stock_id,))
        conn.commit()