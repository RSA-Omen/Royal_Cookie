from ingredient_db import IngredientDB

class IngredientLogic:
    @staticmethod
    def get_ingredients():
        return IngredientDB.get_ingredients()

    @staticmethod
    def add_ingredient(name, size, metadata_id):
        IngredientDB.add_ingredient(name, size, metadata_id)

    @staticmethod
    def update_ingredient(ingredient_id, name, size, metadata_id):
        IngredientDB.update_ingredient(ingredient_id, name, size, metadata_id)

    @staticmethod
    def delete_ingredient(ingredient_id):
        IngredientDB.delete_ingredient(ingredient_id)