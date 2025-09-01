from db import get_connection

class RecipeDB:

    @staticmethod
    def calculate_cost_per_batch(recipe_id):
        """
        Calculates the total cost per batch for a recipe using the latest purchase price and ingredient size for each ingredient.
        Returns the total cost (float).
        """
        from purchases_db import PurchaseDB
        from ingredient_db import IngredientDB
        ingredients = RecipeDB.get_recipe_ingredients(recipe_id)
        total_cost = 0.0
        for ing in ingredients:
            # ing: (ri.id, ri.recipe_id, ri.metadata_id, ri.quantity, ri.unit, m.name)
            metadata_id = ing[2]
            quantity_needed = ing[3]
            # Find all ingredient_ids for this metadata_id
            ingredient_ids = [i["ID"] for i in IngredientDB.get_ingredients() if i["MetadataID"] == metadata_id]
            unit_cost = 0
            for iid in ingredient_ids:
                from db import get_connection
                conn = get_connection()
                cur = conn.cursor()
                cur.execute("SELECT price FROM ingredient_purchases WHERE ingredient_id = ? AND price IS NOT NULL ORDER BY date DESC, id DESC LIMIT 1", (iid,))
                row = cur.fetchone()
                conn.close()
                if row:
                    price = row[0]
                    ing_obj = IngredientDB.get_ingredient_by_id(iid)
                    size = ing_obj["Size"] if ing_obj and "Size" in ing_obj else None
                    if size and size > 0:
                        unit_cost = price / size
                        break
            total_cost += unit_cost * quantity_needed
        return total_cost

    @staticmethod
    def store_cost_per_batch(recipe_id, batch_cost):
        """
        Stores the calculated batch cost in a new table recipe_costs (recipe_id, batch_cost, date).
        """
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS recipe_costs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                recipe_id INTEGER NOT NULL,
                batch_cost REAL NOT NULL,
                calculated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (recipe_id) REFERENCES recipes(id)
            )
        """)
        cur.execute("INSERT INTO recipe_costs (recipe_id, batch_cost) VALUES (?, ?)", (recipe_id, batch_cost))
        conn.commit()
        conn.close()
    @staticmethod
    def init_recipe_db(conn):
        cur = conn.cursor()
        # Recipes table with standard_price_per_unit
        cur.execute("""
            CREATE TABLE IF NOT EXISTS recipes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                output_quantity INTEGER NOT NULL,
                standard_price_per_unit REAL DEFAULT 10.0
            )
        """)

        # Add column if missing (for migrations)
        cur.execute("PRAGMA table_info(recipes)")
        columns = [row[1] for row in cur.fetchall()]
        if "standard_price_per_unit" not in columns:
            cur.execute("ALTER TABLE recipes ADD COLUMN standard_price_per_unit REAL DEFAULT 10.0")

        # Recipe ingredients table (metadata reference)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS recipe_ingredients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                recipe_id INTEGER NOT NULL,
                metadata_id INTEGER NOT NULL,
                quantity REAL NOT NULL,
                unit TEXT,
                FOREIGN KEY(recipe_id) REFERENCES recipes(id) ON DELETE CASCADE,
                FOREIGN KEY(metadata_id) REFERENCES metadata(id)
            )
        """)
        conn.commit()

        # Update all existing recipes to R10 if not set
        cur.execute("UPDATE recipes SET standard_price_per_unit = 10.0 WHERE standard_price_per_unit IS NULL")
        conn.commit()

    # ------------------ Recipe Methods ------------------
    @staticmethod
    def add_recipe(name, output_quantity, standard_price_per_unit=10.0):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO recipes (name, output_quantity, standard_price_per_unit) VALUES (?, ?, ?)",
                    (name, output_quantity, standard_price_per_unit))
        conn.commit()
        rid = cur.lastrowid
        conn.close()
        return rid

    @staticmethod
    def get_all_recipes():
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, name, output_quantity, standard_price_per_unit FROM recipes")
        rows = cur.fetchall()
        conn.close()
        return rows

    @staticmethod
    def update_recipe(recipe_id, name, output_quantity, standard_price_per_unit):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("UPDATE recipes SET name=?, output_quantity=?, standard_price_per_unit=? WHERE id=?",
                    (name, output_quantity, standard_price_per_unit, recipe_id))
        conn.commit()
        conn.close()

    @staticmethod
    def delete_recipe(recipe_id):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM recipes WHERE id=?", (recipe_id,))
        conn.commit()
        conn.close()

    # ------------------ Recipe Ingredient Methods ------------------
    @staticmethod
    def add_recipe_ingredient(recipe_id, metadata_id, quantity, unit):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO recipe_ingredients (recipe_id, metadata_id, quantity, unit)
            VALUES (?, ?, ?, ?)
        """, (recipe_id, metadata_id, quantity, unit))
        conn.commit()
        conn.close()

    @staticmethod
    def get_recipe_ingredients(recipe_id):
        """
        Fetch ingredients for a recipe, showing metadata tag name instead of actual ingredient.
        """
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT ri.id, ri.recipe_id, ri.metadata_id, ri.quantity, ri.unit, m.name
            FROM recipe_ingredients ri
            JOIN metadata m ON ri.metadata_id = m.id
            WHERE ri.recipe_id = ?
        """, (recipe_id,))
        rows = cur.fetchall()
        conn.close()
        return rows

    @staticmethod
    def update_recipe_ingredient(ri_id, quantity, unit):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("UPDATE recipe_ingredients SET quantity=?, unit=? WHERE id=?",
                    (quantity, unit, ri_id))
        conn.commit()
        conn.close()

    @staticmethod
    def delete_recipe_ingredient(ri_id):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM recipe_ingredients WHERE id=?", (ri_id,))
        conn.commit()
        conn.close()
