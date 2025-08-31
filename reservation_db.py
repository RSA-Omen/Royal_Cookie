from db import get_connection

class ReservationDB:
    @staticmethod
    def get_reserved_qty_for_order(order_id, metadata_id):
        """Return the total reserved quantity for a given order and metadata_id (ingredient)."""
        from line_item_db import LineItemDB
        conn = get_connection()
        cursor = conn.cursor()
        # Get all lineitem_ids for this order
        lineitems = LineItemDB.get_order_items(order_id)
        lineitem_ids = [li[0] for li in lineitems]
        if not lineitem_ids:
            conn.close()
            return 0
        # Join reservations -> stock -> ingredients to filter by metadata_id
        q = f'''
            SELECT SUM(r.qty)
            FROM reservations r
            JOIN stock s ON r.ingredient_stock_id = s.id
            JOIN ingredients i ON s.ingredient_id = i.id
            WHERE r.lineitem_id IN ({','.join(['?']*len(lineitem_ids))})
              AND i.metadata_id = ?
        '''
        params = lineitem_ids + [metadata_id]
        cursor.execute(q, params)
        row = cursor.fetchone()
        conn.close()
        return row[0] if row and row[0] is not None else 0
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
    def get_reservation(reservation_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, lineitem_id, ingredient_stock_id, qty, status, reserved_at, reserved_until FROM reservations WHERE id=?",
            (reservation_id,)
        )
        row = cursor.fetchone()
        conn.close()
        if row:
            return {
                "ID": row[0],
                "LineItemID": row[1],
                "IngredientStockID": row[2],
                "Qty": row[3],
                "Status": row[4],
                "ReservedAt": row[5],
                "ReservedUntil": row[6],
            }
        return None

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