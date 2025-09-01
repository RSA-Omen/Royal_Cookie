from PyQt5 import QtWidgets
from recipe_db import RecipeDB

class RecipeProfitabilityUI(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Recipe Profitability Analysis")
        self.resize(800, 500)
        layout = QtWidgets.QVBoxLayout(self)

        # Table for recipes and profitability
        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Recipe Name", "Batch Size", "Batch Cost", "Unit Cost", "Standard Price/Unit (click to edit)", "Profit/Batch"
        ])
        self.table.cellDoubleClicked.connect(self.handle_cell_double_click)
        self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        layout.addWidget(self.table)


        # Details table for ingredient breakdown
        self.details_label = QtWidgets.QLabel("Ingredient Cost Breakdown (select a recipe above)")
        self.details_label.setToolTip("Ingredient purchases must be entered as: total price paid for the batch, and total batch size (e.g., 5000g for R100). The system will calculate price per unit as price / quantity.")
        layout.addWidget(self.details_label)
        self.details_table = QtWidgets.QTableWidget()
        self.details_table.setColumnCount(4)
        self.details_table.setHorizontalHeaderLabels([
            "Ingredient", "Quantity Used", "Unit Cost", "Total Cost"
        ])
        self.details_table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        layout.addWidget(self.details_table)

        self.refresh_btn = QtWidgets.QPushButton("Refresh Profitability")
        self.refresh_btn.clicked.connect(self.refresh_table)
        layout.addWidget(self.refresh_btn)

        self.table.cellClicked.connect(self.show_ingredient_breakdown)
        self.refresh_table()

    def refresh_table(self):
        from recipe_db import RecipeDB
        self.table.setRowCount(0)
        recipes = RecipeDB.get_all_recipes()
        for recipe in recipes:
            recipe_id, name, batch_size, standard_price_per_unit = recipe
            batch_cost = RecipeDB.calculate_cost_per_batch(recipe_id)
            unit_cost = batch_cost / batch_size if batch_size else 0
            profit_per_batch = (standard_price_per_unit * batch_size) - batch_cost
            row_data = [
                name,
                str(batch_size),
                f"R{batch_cost:.2f}",
                f"R{unit_cost:.2f}",
                f"R{standard_price_per_unit:.2f}",
                f"R{profit_per_batch:.2f}"
            ]
            row_idx = self.table.rowCount()
            self.table.insertRow(row_idx)
            for col_idx, value in enumerate(row_data):
                self.table.setItem(row_idx, col_idx, QtWidgets.QTableWidgetItem(str(value)))

    def handle_cell_double_click(self, row, column):
        # Only allow editing the Standard Price/Unit column
        if column != 4:
            return
        recipe_name = self.table.item(row, 0).text()
        from recipe_db import RecipeDB
        recipes = RecipeDB.get_all_recipes()
        recipe_id = None
        batch_size = None
        for r in recipes:
            if r[1] == recipe_name:
                recipe_id = r[0]
                batch_size = r[2]
                break
        if recipe_id is None:
            return
        current_price = float(self.table.item(row, 4).text().replace('R',''))
        new_price, ok = QtWidgets.QInputDialog.getDouble(self, "Edit Standard Price/Unit", f"Set new standard price per unit for {recipe_name}", current_price, 0, 10000, 2)
        if ok:
            RecipeDB.update_recipe(recipe_id, recipe_name, batch_size, new_price)
            self.refresh_table()

    def show_ingredient_breakdown(self, row, column):
        from recipe_db import RecipeDB
        from purchases_db import PurchaseDB
        from ingredient_db import IngredientDB
        recipe_name = self.table.item(row, 0).text()
        # Find recipe_id by name (assumes unique names)
        recipes = RecipeDB.get_all_recipes()
        recipe_id = None
        for r in recipes:
            if r[1] == recipe_name:
                recipe_id = r[0]
                break
        if recipe_id is None:
            self.details_table.setRowCount(0)
            return
        ingredients = RecipeDB.get_recipe_ingredients(recipe_id)
        self.details_table.setRowCount(0)
        for ing in ingredients:
            # ing: (ri.id, ri.recipe_id, ri.metadata_id, ri.quantity, ri.unit, m.name)
            ingredient_name = ing[5]
            quantity_needed = ing[3]
            # Find all ingredient_ids for this metadata_id
            ingredient_ids = [i["ID"] for i in IngredientDB.get_ingredients() if i["MetadataID"] == ing[2]]
            unit_cost = 0
            for iid in ingredient_ids:
                from purchases_db import PurchaseDB
                conn = None
                from db import get_connection
                conn = get_connection()
                cur = conn.cursor()
                cur.execute("SELECT price FROM ingredient_purchases WHERE ingredient_id = ? AND price IS NOT NULL ORDER BY date DESC, id DESC LIMIT 1", (iid,))
                row = cur.fetchone()
                conn.close()
                if row:
                    price = row[0]
                    # Get the ingredient size (e.g., 5000g for the batch)
                    ing_obj = IngredientDB.get_ingredient_by_id(iid)
                    size = ing_obj["Size"] if ing_obj and "Size" in ing_obj else None
                    if size and size > 0:
                        unit_cost = price / size
                        print(f"DEBUG: Ingredient {ingredient_name} purchase: price={price}, size={size}, unit_cost={unit_cost}")
                        break
            total_cost = unit_cost * quantity_needed
            row_idx = self.details_table.rowCount()
            self.details_table.insertRow(row_idx)
            self.details_table.setItem(row_idx, 0, QtWidgets.QTableWidgetItem(str(ingredient_name)))
            self.details_table.setItem(row_idx, 1, QtWidgets.QTableWidgetItem(str(quantity_needed)))
            self.details_table.setItem(row_idx, 2, QtWidgets.QTableWidgetItem(f"R{unit_cost:.2f}"))
            self.details_table.setItem(row_idx, 3, QtWidgets.QTableWidgetItem(f"R{total_cost:.2f}"))

    def get_standard_price_per_unit(self, recipe_id):
        from recipe_db import RecipeDB
        recipes = RecipeDB.get_all_recipes()
        for r in recipes:
            if r[0] == recipe_id:
                return r[3]
        return 10.0

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = RecipeProfitabilityUI()
    window.show()
    sys.exit(app.exec_())
