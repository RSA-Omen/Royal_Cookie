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

    @staticmethod
    def get_ingredients_for_recipe(recipe_id):
        """
        Returns a list of tuples:
        (ingredient_id, ingredient_name, amount_per_recipe)
        """
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT i.id, i.name, ri.amount
                FROM recipe_ingredients ri
                JOIN ingredients i ON ri.ingredient_id = i.id
                WHERE ri.recipe_id = ?
            """, (recipe_id,))
            ingredients = cur.fetchall()
            conn.close()
            return ingredients
        except Exception as e:
            print(f"[ERROR] Failed to fetch ingredients for recipe {recipe_id}: {e}")
            return []

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

