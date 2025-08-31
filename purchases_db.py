from db import get_connection

class PurchaseDB:
    @staticmethod
    def init_ingredient_purchases_db(conn):
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ingredient_purchases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ingredient_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                quantity REAL NOT NULL,
                price REAL,
                discount REAL DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (ingredient_id) REFERENCES ingredients(id)
            )
        ''')
        conn.commit()

    @staticmethod
    def get_purchases(ingredient_id=None):
        conn = get_connection()
        cur = conn.cursor()
        if ingredient_id:
            cur.execute("SELECT * FROM ingredient_purchases WHERE ingredient_id = ?", (ingredient_id,))
        else:
            cur.execute("SELECT * FROM ingredient_purchases")
        rows = cur.fetchall()
        conn.close()
        return rows

    @staticmethod
    def add_purchase(ingredient_id, date, quantity, price, discount):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO ingredient_purchases (ingredient_id, date, quantity, price, discount) VALUES (?, ?, ?, ?, ?)",
            (ingredient_id, date, quantity, price, discount)
        )
        conn.commit()
        conn.close()

    @staticmethod
    def update_purchase(purchase_id, quantity, price, discount):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "UPDATE ingredient_purchases SET quantity=?, price=?, discount=? WHERE id=?",
            (quantity, price, discount, purchase_id)
        )
        conn.commit()
        conn.close()

    @staticmethod
    def delete_purchase(purchase_id):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM ingredient_purchases WHERE id=?", (purchase_id,))
        conn.commit()
        conn.close()
