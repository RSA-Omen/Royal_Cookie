from db import get_connection

class ReservationDB:
    @staticmethod
    def init_reservations_db(conn):
        """
        Initialize the reservations table.
        Each reservation links a line item to a specific stock batch (ingredient_stock).
        """
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reservations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                lineitem_id INTEGER NOT NULL,
                ingredient_stock_id INTEGER NOT NULL,
                qty REAL NOT NULL,
                status TEXT DEFAULT 'active',
                reserved_at TEXT DEFAULT CURRENT_TIMESTAMP,
                reserved_until TEXT,
                FOREIGN KEY (lineitem_id) REFERENCES line_items(id),
                FOREIGN KEY (ingredient_stock_id) REFERENCES stock(id)
            )
        ''')
        conn.commit()

    @staticmethod
    def add_reservation(lineitem_id, ingredient_stock_id, qty, status='active', reserved_until=None):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO reservations (lineitem_id, ingredient_stock_id, qty, status, reserved_until) VALUES (?, ?, ?, ?, ?)',
            (lineitem_id, ingredient_stock_id, qty, status, reserved_until)
        )
        conn.commit()
        conn.close()

    @staticmethod
    def get_reservations_for_lineitem(lineitem_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, lineitem_id, ingredient_stock_id, qty, status, reserved_at, reserved_until FROM reservations WHERE lineitem_id=?",
            (lineitem_id,)
        )
        rows = cursor.fetchall()
        conn.close()
        return [
            {
                "ID": r[0],
                "LineItemID": r[1],
                "IngredientStockID": r[2],
                "Qty": r[3],
                "Status": r[4],
                "ReservedAt": r[5],
                "ReservedUntil": r[6],
            }
            for r in rows
        ]

    @staticmethod
    def update_reservation(reservation_id, qty=None, status=None, reserved_until=None):
        conn = get_connection()
        cursor = conn.cursor()
        updates = []
        params = []
        if qty is not None:
            updates.append("qty=?")
            params.append(qty)
        if status is not None:
            updates.append("status=?")
            params.append(status)
        if reserved_until is not None:
            updates.append("reserved_until=?")
            params.append(reserved_until)
        params.append(reservation_id)
        cursor.execute(
            f"UPDATE reservations SET {', '.join(updates)} WHERE id=?",
            tuple(params)
        )
        conn.commit()
        conn.close()

    @staticmethod
    def delete_reservation(reservation_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM reservations WHERE id=?",
            (reservation_id,)
        )
        conn.commit()
        conn.close()