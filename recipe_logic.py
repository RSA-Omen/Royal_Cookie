from recipe_db import RecipeDB

class RecipeLogic:
    @staticmethod
    def get_all_recipes():
        return RecipeDB.get_all_recipes()

    @staticmethod
    def add_recipe(name, output_quantity):
        if not name or not name.strip():
            raise ValueError("Recipe name cannot be empty.")
        if not isinstance(output_quantity, (int, float)) or output_quantity < 1:
            raise ValueError("Output quantity must be at least 1.")
        return RecipeDB.add_recipe(name.strip(), int(output_quantity))

    @staticmethod
    def update_recipe(recipe_id, name, output_quantity):
        if not name or not name.strip():
            raise ValueError("Recipe name cannot be empty.")
        if not isinstance(output_quantity, (int, float)) or output_quantity < 1:
            raise ValueError("Output quantity must be at least 1.")
        RecipeDB.update_recipe(recipe_id, name.strip(), int(output_quantity))

    @staticmethod
    def delete_recipe(recipe_id):
        RecipeDB.delete_recipe(recipe_id)

    @staticmethod
    def get_recipe_ingredients(recipe_id):
        return RecipeDB.get_recipe_ingredients(recipe_id)

    @staticmethod
    def add_recipe_ingredient(recipe_id, metadata_id, quantity, unit):
        # Validate quantity
        if not isinstance(quantity, (int, float)) or quantity <= 0:
            raise ValueError("Quantity must be a positive number.")
        # Validate unit against metadata
        from metadata_db import MetadataDB
        metadata = [m for m in MetadataDB.get_all_metadata() if m[0] == metadata_id]
        if not metadata:
            raise ValueError("Invalid metadata ID.")
        expected_unit = metadata[0][3]
        if unit.strip() != expected_unit:
            raise ValueError(f"Unit must match metadata unit: {expected_unit}")
        RecipeDB.add_recipe_ingredient(recipe_id, metadata_id, quantity, unit.strip())

    @staticmethod
    def update_recipe_ingredient(ri_id, quantity, unit):
        # Validate quantity
        if not isinstance(quantity, (int, float)) or quantity <= 0:
            raise ValueError("Quantity must be a positive number.")
        # Get metadata_id for this recipe_ingredient
        from recipe_db import RecipeDB
        from metadata_db import MetadataDB
        # Find the recipe_ingredient row
        recipe_ingredients = []
        # Try to get all recipe_ingredients for all recipes (inefficient, but safe for now)
        # We'll search for the one with ri_id
        import sqlite3
        conn = None
        try:
            from db import get_connection
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("SELECT metadata_id FROM recipe_ingredients WHERE id=?", (ri_id,))
            row = cur.fetchone()
            if not row:
                raise ValueError("Recipe ingredient not found.")
            metadata_id = row[0]
        finally:
            if conn:
                conn.close()
        metadata = [m for m in MetadataDB.get_all_metadata() if m[0] == metadata_id]
        if not metadata:
            raise ValueError("Invalid metadata ID.")
        expected_unit = metadata[0][3]
        if unit.strip() != expected_unit:
            raise ValueError(f"Unit must match metadata unit: {expected_unit}")
        RecipeDB.update_recipe_ingredient(ri_id, quantity, unit.strip())

    @staticmethod
    def delete_recipe_ingredient(ri_id):
        RecipeDB.delete_recipe_ingredient(ri_id)