# seeding_data.py
from init_all import init_db
from db import get_connection
from metadata_db import MetadataDB
from ingredient_db import IngredientDB
from recipe_db import RecipeDB
from ingredient_history_db import IngredientHistoryDB
from ingredient_stock_db import IngredientStockDB
from datetime import datetime

def drop_all_tables(conn):
    cur = conn.cursor()
    print("Dropping all tables...")
    cur.execute("DROP TABLE IF EXISTS recipe_ingredients")
    cur.execute("DROP TABLE IF EXISTS recipes")
    cur.execute("DROP TABLE IF EXISTS ingredients")
    cur.execute("DROP TABLE IF EXISTS metadata")
    cur.execute("DROP TABLE IF EXISTS ingredient_history")
    cur.execute("DROP TABLE IF EXISTS ingredient_stock")
    conn.commit()

def init_all_tables(conn):
    print("Initializing tables...")
    MetadataDB.init_metadata_db(conn)
    IngredientDB.init_ingredient_db(conn)
    RecipeDB.init_recipe_db(conn)
    IngredientHistoryDB.init_ingredient_history_db(conn)
    IngredientStockDB.init_ingredient_stock_db(conn)

def seed_metadata():
    metadata_tags = [
        ("Sugar", "Sweetener"),
        ("Butter", "Fat"),
        ("Eggs", "Binder"),
        ("Chocolate", "Flavoring"),
        ("Flour", "Base")
    ]
    print("Seeding metadata...")
    for name, desc in metadata_tags:
        try:
            MetadataDB.add_metadata(name, desc)
            print(f"Metadata seeded: {name}")
        except Exception as e:
            print(f"Skipped {name}: {e}")

def seed_ingredients():
    ingredients = [
        ("White Sugar", 500, "g", "Sugar"),
        ("Brown Sugar", 300, "g", "Sugar"),
        ("Butter Block", 250, "g", "Butter"),
        ("Large Eggs", 6, "pcs", "Eggs"),
        ("Dark Chocolate Bar", 200, "g", "Chocolate"),
        ("All Purpose Flour", 1000, "g", "Flour")
    ]
    print("Seeding ingredients...")
    metadata_list = MetadataDB.get_all_metadata()
    metadata_map = {name: mid for mid, name, _ in metadata_list}

    for name, size, unit, meta_name in ingredients:
        meta_id = metadata_map.get(meta_name)
        if not meta_id:
            print(f"Metadata not found for {name}, skipping")
            continue
        try:
            IngredientDB.add_ingredient(name, size, unit, meta_id)
            print(f"Ingredient seeded: {name}")
        except Exception as e:
            print(f"Skipped {name}: {e}")

def seed_recipes():
    recipes = [
        ("Chocolate Cake", 12, [("All Purpose Flour", 200, "g"),
                                ("White Sugar", 150, "g"),
                                ("Butter Block", 100, "g"),
                                ("Large Eggs", 3, "pcs"),
                                ("Dark Chocolate Bar", 100, "g")]),
        ("Chocolate Chip Cookies", 24, [("All Purpose Flour", 250, "g"),
                                        ("Brown Sugar", 100, "g"),
                                        ("Butter Block", 125, "g"),
                                        ("Large Eggs", 2, "pcs"),
                                        ("Dark Chocolate Bar", 150, "g")]),
        ("Butter Cookies", 20, [("All Purpose Flour", 200, "g"),
                                ("Butter Block", 150, "g"),
                                ("White Sugar", 100, "g"),
                                ("Large Eggs", 2, "pcs")])
    ]
    print("Seeding recipes...")
    ing_list = IngredientDB.get_ingredients()
    ing_map = {ing["Name"]: ing["ID"] for ing in ing_list}

    for recipe_name, output_qty, ing_items in recipes:
        try:
            recipe_id = RecipeDB.add_recipe(recipe_name, output_qty)
            print(f"Recipe seeded: {recipe_name}")
        except Exception as e:
            print(f"Skipped recipe {recipe_name}: {e}")
            continue

        for ing_name, qty, unit in ing_items:
            ing_id = ing_map.get(ing_name)
            if not ing_id:
                print(f"Ingredient {ing_name} not found for {recipe_name}, skipping")
                continue
            try:
                RecipeDB.add_recipe_ingredient(recipe_id, ing_id, qty, unit)
            except Exception as e:
                print(f"Skipped ingredient link {ing_name} for {recipe_name}: {e}")

def seed_stock_and_history():
    print("Seeding ingredient stock/history...")
    ing_list = IngredientDB.get_ingredients()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for ing in ing_list:
        try:
            # Seed 3 history entries per ingredient
            for qty in [100, 200, 150]:
                IngredientHistoryDB.add_history(ing["ID"], now, qty, price=10.0, discount=0.0)

            # Set current stock as sum of seeded quantities
            total_qty = sum([100, 200, 150])
            IngredientStockDB.add_stock(ing["ID"], total_qty)

            print(f"Stock seeded for: {ing['Name']}")
        except Exception as e:
            print(f"Skipped stock for {ing['Name']}: {e}")

def main():
    init_db()  # Ensure DB is initialized
    conn = get_connection()
    drop_all_tables(conn)
    init_all_tables(conn)
    seed_metadata()
    seed_ingredients()
    seed_recipes()
    seed_stock_and_history()
    conn.close()
    print("Seeding complete!")

if __name__ == "__main__":
    main()
