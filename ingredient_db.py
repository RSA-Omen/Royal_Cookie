from db import get_connection

class IngredientDB:
    @staticmethod
    def init_ingredient_db(conn):
        """
        Initialize the ingredients table linked to metadata.
        Removes the unit column (unit is now in metadata).
        """
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ingredients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                size REAL NOT NULL,
                metadata_id INTEGER NOT NULL,
                FOREIGN KEY(metadata_id) REFERENCES metadata(id)
            )
        ''')
        conn.commit()

    @staticmethod
    def add_ingredient(name, size, metadata_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO ingredients (name, size, metadata_id) VALUES (?, ?, ?)',
            (name, size, metadata_id)
        )
        conn.commit()
        conn.close()

    @staticmethod
    def get_ingredients():
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, size, metadata_id FROM ingredients")
        rows = cursor.fetchall()
        conn.close()

        ingredients = []
        for r in rows:
            ingredients.append({
                "ID": r[0],
                "Name": r[1],
                "Size": r[2],
                "MetadataID": r[3],
            })
        return ingredients

    @staticmethod
    def get_ingredient_by_id(ingredient_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, size, metadata_id FROM ingredients WHERE id=?", (ingredient_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return {
                "ID": row[0],
                "Name": row[1],
                "Size": row[2],
                "MetadataID": row[3],
            }
        return None

    @staticmethod
    def update_ingredient(ingredient_id, name, size, metadata_id):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            'UPDATE ingredients SET name=?, size=?, metadata_id=? WHERE id=?',
            (name, size, metadata_id, ingredient_id)
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