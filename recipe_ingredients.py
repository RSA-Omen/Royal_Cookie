from db import get_connection

class RecipeIngredientDB:
    @staticmethod
    def init_recipe_ingredients_db(connection):
        """
        Initialize the recipe_ingredients table.
        Each row links a recipe to a metadata ingredient and specifies the quantity needed.
        """
        cursor = connection.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS recipe_ingredients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                recipe_id INTEGER NOT NULL,
                metadata_id INTEGER NOT NULL,
                quantity REAL NOT NULL,
                FOREIGN KEY (recipe_id) REFERENCES recipes(id),
                FOREIGN KEY (metadata_id) REFERENCES metadata(id)
            )
        ''')
        connection.commit()

    @staticmethod
    def add_recipe_ingredient(recipe_id, metadata_id, quantity):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO recipe_ingredients (recipe_id, metadata_id, quantity) VALUES (?, ?, ?)',
            (recipe_id, metadata_id, quantity)
        )
        conn.commit()
        conn.close()

    @staticmethod
    def get_ingredients_for_recipe(recipe_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, recipe_id, metadata_id, quantity FROM recipe_ingredients WHERE recipe_id=?",
            (recipe_id,)
        )
        rows = cursor.fetchall()
        conn.close()
        return [
            {
                "ID": r[0],
                "RecipeID": r[1],
                "MetadataID": r[2],
                "Quantity": r[3],
            }
            for r in rows
        ]

    @staticmethod
    def update_recipe_ingredient(recipe_ingredient_id, quantity):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE recipe_ingredients SET quantity=? WHERE id=?",
            (quantity, recipe_ingredient_id)
        )
        conn.commit()
        conn.close()

    @staticmethod
    def delete_recipe_ingredient(recipe_ingredient_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM recipe_ingredients WHERE id=?",
            (recipe_ingredient_id,)
        )
        conn.commit()
        conn.close()