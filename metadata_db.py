from db import get_connection

class MetadataDB:
    @staticmethod
    def init_metadata_db(conn):
        """Create the metadata table with a unit column."""
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS metadata (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                description TEXT,
                unit TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

    @staticmethod
    def add_metadata(name, description, unit):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO metadata (name, description, unit) VALUES (?, ?, ?)",
            (name, description, unit)
        )
        conn.commit()
        rid = cur.lastrowid
        conn.close()
        return rid

    @staticmethod
    def get_all_metadata():
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, name, description, unit FROM metadata")
        rows = cur.fetchall()
        conn.close()
        return rows

    @staticmethod
    def update_metadata(metadata_id, name, description, unit):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "UPDATE metadata SET name=?, description=?, unit=? WHERE id=?",
            (name, description, unit, metadata_id)
        )
        conn.commit()
        conn.close()    

    @staticmethod
    def delete_metadata(metadata_id):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM metadata WHERE id=?", (metadata_id,))
        conn.commit()
        conn.close()