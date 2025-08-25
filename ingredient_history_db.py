from db import get_connection

class IngredientHistoryDB:
    @staticmethod
    def init_ingredient_history_db(conn):
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ingredient_history (
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
    def get_history(ingredient_id=None):
        conn = get_connection()
        cur = conn.cursor()
        if ingredient_id:
            cur.execute("SELECT * FROM ingredient_history WHERE ingredient_id = ?", (ingredient_id,))
        else:
            cur.execute("SELECT * FROM ingredient_history")
        rows = cur.fetchall()
        conn.close()
        return rows

    @staticmethod
    def add_history(ingredient_id, date, quantity, price, discount):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO ingredient_history (ingredient_id, date, quantity, price, discount) VALUES (?, ?, ?, ?, ?)",
            (ingredient_id, date, quantity, price, discount)
        )
        conn.commit()
        conn.close()

    @staticmethod
    def update_history(history_id, quantity, price, discount):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "UPDATE ingredient_history SET quantity=?, price=?, discount=? WHERE id=?",
            (quantity, price, discount, history_id)
        )
        conn.commit()
        conn.close()

    @staticmethod
    def delete_history(history_id):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM ingredient_history WHERE id=?", (history_id,))
        conn.commit()
        conn.close()
