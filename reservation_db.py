from db import get_connection

class ReservationDB:
    @staticmethod
    def init_reservations_table(connection):
        """Create the reservations table if it doesn't exist."""
        try:
            cur = connection.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS reservations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_id INTEGER NOT NULL,
                    lineitem_id INTEGER NOT NULL,
                    metadata_id INTEGER NOT NULL,
                    qty REAL NOT NULL,
                    reserved_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    reserved_until TEXT,
                    status TEXT DEFAULT 'active',
                    FOREIGN KEY(order_id) REFERENCES orders(id),
                    FOREIGN KEY(lineitem_id) REFERENCES line_items(id),
                    FOREIGN KEY(metadata_id) REFERENCES metadata(id)
                )
            """)
            connection.commit()
        except Exception as e:
            print(f"[ERROR] Failed to initialize reservations table: {e}")

    @staticmethod
    def add_reservation(order_id, lineitem_id, metadata_id, qty, reserved_until=None):
        """Add a new reservation."""
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO reservations (order_id, lineitem_id, metadata_id, qty, reserved_until)
                VALUES (?, ?, ?, ?, ?)
            """, (order_id, lineitem_id, metadata_id, qty, reserved_until))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"[ERROR] Failed to add reservation: {e}")

    @staticmethod
    def get_reservations(order_id=None, status='active'):
        """Get reservations, optionally filtered by order and status."""
        try:
            conn = get_connection()
            cur = conn.cursor()
            if order_id:
                cur.execute("""
                    SELECT * FROM reservations WHERE order_id=? AND status=?
                """, (order_id, status))
            else:
                cur.execute("""
                    SELECT * FROM reservations WHERE status=?
                """, (status,))
            rows = cur.fetchall()
            conn.close()
            return rows
        except Exception as e:
            print(f"[ERROR] Failed to fetch reservations: {e}")
            return []

    @staticmethod
    def release_reservation(reservation_id):
        """Mark a reservation as released."""
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("""
                UPDATE reservations SET status='released' WHERE id=?
            """, (reservation_id,))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"[ERROR] Failed to release reservation: {e}")

    @staticmethod
    def get_reserved_qty(metadata_id):
        """Get total reserved quantity for a given ingredient (metadata_id)."""
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT SUM(qty) FROM reservations
                WHERE metadata_id=? AND status='active'
            """, (metadata_id,))
            result = cur.fetchone()
            conn.close()
            return result[0] or 0
        except Exception as e:
            print(f"[ERROR] Failed to get reserved qty: {e}")
            return 0
    
    @staticmethod
    def get_reserved_qty_for_order(order_id, metadata_id):
        """Get total reserved quantity for a given ingredient (metadata_id) for a specific order."""
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT SUM(qty) FROM reservations
                WHERE metadata_id=? AND order_id=? AND status='active'
            """, (metadata_id, order_id))
            result = cur.fetchone()
            conn.close()
            return result[0] or 0
        except Exception as e:
            print(f"[ERROR] Failed to get reserved qty for order: {e}")
            return 0