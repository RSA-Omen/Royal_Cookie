from db import get_connection

class MetadataDB:
    @staticmethod
    def init_metadata_db(conn):
        """Create the metadata table."""
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS metadata (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- ADDED: track creation time
            )
        """)
        conn.commit()



    # --- CRUD Methods ---
    # In MetadataDB
    @staticmethod
    def get_all_metadata():
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, name, description FROM metadata")
        rows = cur.fetchall()
        conn.close()
        return rows

    @staticmethod
    def get_all_metadata_tags():
        return MetadataDB.get_all_metadata()

    @staticmethod
    def add_metadata(name, description):  # was add_metadata_tag
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO metadata (name, description) VALUES (?, ?)",
            (name, description)
        )
        conn.commit()
        rid = cur.lastrowid
        conn.close()
        return rid

    @staticmethod
    def update_metadata(metadata_id, name, description):  # was update_metadata_tag
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "UPDATE metadata SET name=?, description=? WHERE id=?",
            (name, description, metadata_id)
        )
        conn.commit()
        conn.close()

    @staticmethod
    def delete_metadata(metadata_id):  # was delete_metadata_tag
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM metadata WHERE id=?", (metadata_id,))
        conn.commit()
        conn.close()

