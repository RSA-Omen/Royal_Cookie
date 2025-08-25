from PyQt5 import QtWidgets, QtCore
from recipe_db import RecipeDB
from metadata_db import MetadataDB

class RecipesPopup(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Recipe Manager")
        self.resize(800, 500)

        # Layouts
        main_layout = QtWidgets.QHBoxLayout(self)
        left_layout = QtWidgets.QVBoxLayout()
        right_layout = QtWidgets.QVBoxLayout()

        # Recipes list
        self.recipe_list = QtWidgets.QListWidget()
        self.recipe_list.itemSelectionChanged.connect(self.load_recipe_ingredients)
        left_layout.addWidget(QtWidgets.QLabel("Recipes"))
        left_layout.addWidget(self.recipe_list)

        # Recipe buttons
        for text, func in [("Add Recipe", self.add_recipe),
                           ("Edit Recipe", self.edit_recipe),
                           ("Delete Recipe", self.delete_recipe)]:
            btn = QtWidgets.QPushButton(text)
            btn.clicked.connect(func)
            left_layout.addWidget(btn)

        # Recipe Ingredients list
        self.ingredient_list = QtWidgets.QListWidget()
        right_layout.addWidget(QtWidgets.QLabel("Recipe Ingredients (Metadata)"))
        right_layout.addWidget(self.ingredient_list)

        # Ingredient buttons
        for text, func in [("Add Ingredient", self.add_recipe_ingredient),
                           ("Edit Ingredient", self.edit_recipe_ingredient),
                           ("Delete Ingredient", self.delete_recipe_ingredient)]:
            btn = QtWidgets.QPushButton(text)
            btn.clicked.connect(func)
            right_layout.addWidget(btn)

        # Combine layouts
        main_layout.addLayout(left_layout, 1)
        main_layout.addLayout(right_layout, 2)

        # Load recipes
        self.load_recipes()

    # ------------------ Recipes ------------------
    def load_recipes(self):
        self.recipe_list.clear()
        recipes = RecipeDB.get_all_recipes()
        for r in recipes:
            rid = r[0]
            if rid is None: continue
            item = QtWidgets.QListWidgetItem(f"{r[1]} (yields {r[2]})")
            item.setData(QtCore.Qt.UserRole, rid)
            self.recipe_list.addItem(item)

    def add_recipe(self):
        name, ok = QtWidgets.QInputDialog.getText(self, "Add Recipe", "Recipe name:")
        if not ok or not name.strip(): return
        qty, ok2 = QtWidgets.QInputDialog.getInt(self, "Output Quantity", "Units produced:", 1, 1)
        if ok2:
            RecipeDB.add_recipe(name.strip(), qty)
            self.load_recipes()

    def edit_recipe(self):
        selected = self.recipe_list.currentItem()
        if not selected: return
        recipe_id = selected.data(QtCore.Qt.UserRole)
        name, ok = QtWidgets.QInputDialog.getText(self, "Edit Recipe", "Recipe name:", text=selected.text())
        if not ok or not name.strip(): return
        qty, ok2 = QtWidgets.QInputDialog.getInt(self, "Output Quantity", "Units produced:", 1, 1)
        if ok2:
            RecipeDB.update_recipe(recipe_id, name.strip(), qty)
            self.load_recipes()

    def delete_recipe(self):
        selected = self.recipe_list.currentItem()
        if not selected: return
        recipe_id = selected.data(QtCore.Qt.UserRole)
        RecipeDB.delete_recipe(recipe_id)
        self.load_recipes()
        self.ingredient_list.clear()

    # ------------------ Recipe Ingredients ------------------
    def load_recipe_ingredients(self):
        if not hasattr(self, 'ingredient_list'): return
        self.ingredient_list.clear()
        selected = self.recipe_list.currentItem()
        if not selected: return

        recipe_id = selected.data(QtCore.Qt.UserRole)
        if recipe_id is None: return

        try:
            ingredients = RecipeDB.get_recipe_ingredients(recipe_id)
        except Exception as e:
            print("Error loading recipe ingredients:", e)
            ingredients = []

        for ing in ingredients:
            # ing[5] = metadata.name, ing[3]=quantity, ing[4]=unit
            item = QtWidgets.QListWidgetItem(f"{ing[5]} – {ing[3]} {ing[4] or ''}")
            item.setData(QtCore.Qt.UserRole, ing[0])  # recipe_ingredient id
            self.ingredient_list.addItem(item)

    def add_recipe_ingredient(self):
        try:
            selected = self.recipe_list.currentItem()
            if not selected: return
            recipe_id = selected.data(QtCore.Qt.UserRole)
            if recipe_id is None: return

            metadata_tags = MetadataDB.get_all_metadata()
            if not metadata_tags:
                QtWidgets.QMessageBox.warning(self, "Error", "No metadata tags available. Add tags first.")
                return

            items = [f"{m[1]} ({m[2]})" for m in metadata_tags]
            choice, ok = QtWidgets.QInputDialog.getItem(self, "Select Metadata Tag", "Metadata:", items, 0, False)
            if not ok or choice not in items: return
            metadata_id = metadata_tags[items.index(choice)][0]

            qty, ok2 = QtWidgets.QInputDialog.getDouble(self, "Quantity", "Enter quantity:", 1, 0.0)
            if not ok2: return
            unit, ok3 = QtWidgets.QInputDialog.getText(self, "Unit", "Enter unit (e.g., g, ml):")
            if not ok3: return

            # Guard DB call in try/except
            try:
                RecipeDB.add_recipe_ingredient(recipe_id, metadata_id, qty, unit)
            except Exception as e:
                print("Error adding recipe ingredient:", e)
                QtWidgets.QMessageBox.warning(self, "DB Error", str(e))
                return

            self.load_recipe_ingredients()

        except Exception as e_outer:
            print("Unexpected error in add_recipe_ingredient:", e_outer)

    def edit_recipe_ingredient(self):
        selected_ing = self.ingredient_list.currentItem()
        if not selected_ing: return
        ri_id = selected_ing.data(QtCore.Qt.UserRole)
        qty, ok = QtWidgets.QInputDialog.getDouble(self, "Quantity", "Enter new quantity:", 1, 0.0)
        if not ok: return
        unit, ok2 = QtWidgets.QInputDialog.getText(self, "Unit", "Enter new unit:")
        if not ok2: return
        RecipeDB.update_recipe_ingredient(ri_id, qty, unit)
        self.load_recipe_ingredients()

    def delete_recipe_ingredient(self):
        selected_ing = self.ingredient_list.currentItem()
        if not selected_ing: return
        ri_id = selected_ing.data(QtCore.Qt.UserRole)
        RecipeDB.delete_recipe_ingredient(ri_id)
        self.load_recipe_ingredients()
