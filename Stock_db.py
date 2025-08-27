from db import get_connection
from datetime import datetime

class IngredientStockDB:

    @staticmethod
    def init_ingredient_stock_db(conn):
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ingredient_stock (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ingredient_id INTEGER NOT NULL,
                quantity REAL NOT NULL,
                last_updated TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (ingredient_id) REFERENCES ingredients(id)
            )
        ''')
        conn.commit()

    @staticmethod
    def get_stock(ingredient_id=None):
        conn = get_connection()
        cur = conn.cursor()
        if ingredient_id:
            cur.execute("SELECT * FROM ingredient_stock WHERE ingredient_id = ?", (ingredient_id,))
        else:
            cur.execute("SELECT * FROM ingredient_stock")
        rows = cur.fetchall()
        conn.close()
        return rows

    @staticmethod
    def add_stock(ingredient_id, quantity):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO ingredient_stock (ingredient_id, quantity, last_updated) VALUES (?, ?, ?)",
            (ingredient_id, quantity, datetime.now().isoformat())
        )
        conn.commit()
        conn.close()

    @staticmethod
    def get_available_stock(ingredient_id):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT quantity FROM ingredient_stock WHERE ingredient_id=?", (ingredient_id,))
        row = cur.fetchone()
        conn.close()
        return row[0] if row else 0

    @staticmethod
    def update_stock(stock_id, quantity):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "UPDATE ingredient_stock SET quantity=?, last_updated=? WHERE id=?",
            (quantity, datetime.now().isoformat(), stock_id)
        )
        conn.commit()
        conn.close()

    @staticmethod
    def delete_stock(stock_id):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM ingredient_stock WHERE id=?", (stock_id,))
        conn.commit()
        conn.close()
