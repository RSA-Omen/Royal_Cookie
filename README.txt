======================
DBs (Database interaction / CRUD)
======================

CustomerDB
- Handles all database operations related to customers: add, update, delete, fetch.

IngredientsDB
- Manages ingredient definitions: names, units, possibly categories.

Ingredients_historyDB
- Keeps a historical record of ingredient changes or usage.

Ingredients_stockDB
- Tracks current stock levels of ingredients; handles adjustments.

Line_ItemDB
- Manages the items within orders, linking recipes to quantities and orders.

MetadataDB
- Stores auxiliary or configuration data used by the app (e.g., units, statuses).

OrderDB
- Handles orders for customers: create, update, delete, list.

RecipeDB
- Manages recipes: ingredients required, quantities, possibly instructions.


======================
UIs (User interface for interacting with DBs)
======================

CustomerUI
- Interface to view, add, edit, and delete customers; select customers to view orders.

IngredientUI
- Interface for managing ingredients themselves (add, edit, delete ingredient definitions).

Ingredient_stockUI
- Interface for viewing and adjusting ingredient stock levels.

Ingredient_historyUI
- Interface for viewing historical ingredient usage or adjustments.

MetadataUI
- Interface for managing metadata or auxiliary settings used across the app.

orderDialogUI
- Interface for creating or editing orders (selecting recipes, quantities, etc.).

RecipeUI
- Interface for managing recipes: add, edit, delete, view ingredients per recipe.


======================
Utility / Initialization
======================

init_add.py
- Contains routines to initialize or populate the database with default values.

app.py
- Main entry point of the application; launches the UI and connects all modules.
