from db import get_connection

class IngredientDB:
    @staticmethod
    def init_ingredient_db(conn):
        """
        Initialize the ingredients table linked to metadata.
        """
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ingredients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                size REAL NOT NULL,
                unit TEXT NOT NULL,
                metadata_id INTEGER NOT NULL,
                FOREIGN KEY(metadata_id) REFERENCES metadata(id)
            )
        ''')
        conn.commit()

    @staticmethod
    def add_ingredient(name, size, unit, metadata_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO ingredients (name, size, unit, metadata_id) VALUES (?, ?, ?, ?)',
            (name, size, unit, metadata_id)
        )
        conn.commit()
        conn.close()

    @staticmethod
    def get_ingredients():
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, size, unit, metadata_id FROM ingredients")
        rows = cursor.fetchall()
        conn.close()

        ingredients = []
        for r in rows:
            ingredients.append({
                "ID": r[0],
                "Name": r[1],
                "Size": r[2],
                "Unit": r[3],
                "MetadataID": r[4],
            })
        return ingredients

    # alias for compatibility with UI
    @staticmethod
    def get_all_ingredients():
        return IngredientDB.get_ingredients()

    @staticmethod
    def update_ingredient(ingredient_id, name, size, unit, metadata_id):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            'UPDATE ingredients SET name=?, size=?, unit=?, metadata_id=? WHERE id=?',
            (name, size, unit, metadata_id, ingredient_id)
        )
        conn.commit()
        conn.close()

    @staticmethod
    def delete_ingredient(ingredient_id):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM ingredients WHERE id=?", (ingredient_id,))
        conn.commit()
        conn.close()
