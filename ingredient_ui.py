from PyQt5 import QtWidgets
from ingredient_db import IngredientDB
from metadata_db import MetadataDB

class IngredientsPopup(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Manage Ingredients")
        self.resize(600, 400)

        # Data
        self.data = []
        self.metadata_list = []

        # --- Buttons ---
        btn_layout = QtWidgets.QHBoxLayout()
        self.add_btn = QtWidgets.QPushButton("Add")
        self.update_btn = QtWidgets.QPushButton("Update")
        self.delete_btn = QtWidgets.QPushButton("Delete")
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.update_btn)
        btn_layout.addWidget(self.delete_btn)

        # --- Inputs ---
        form_layout = QtWidgets.QHBoxLayout()
        self.name_input = QtWidgets.QLineEdit(); self.name_input.setPlaceholderText("Name")
        self.size_input = QtWidgets.QLineEdit(); self.size_input.setPlaceholderText("Size")
        self.unit_input = QtWidgets.QLineEdit(); self.unit_input.setPlaceholderText("Unit")
        self.meta_input = QtWidgets.QComboBox()
        form_layout.addWidget(self.name_input)
        form_layout.addWidget(self.size_input)
        form_layout.addWidget(self.unit_input)
        form_layout.addWidget(self.meta_input)

        # --- Table ---
        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Name", "Size", "Unit", "Metadata"])
        self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

        # --- Layout ---
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addLayout(btn_layout)
        main_layout.addLayout(form_layout)
        main_layout.addWidget(self.table)

        # --- Connect Buttons ---
        self.add_btn.clicked.connect(self.add_ingredient)
        self.update_btn.clicked.connect(self.update_ingredient)
        self.delete_btn.clicked.connect(self.delete_ingredient)
        self.table.cellClicked.connect(self.fill_form)

        # --- Load metadata and table ---
        self.load_metadata()
        self.refresh_table()

    def load_metadata(self):
        """Load metadata tags into combo box with debug prints."""
        try:
            self.metadata_list = MetadataDB.get_all_metadata()
            print("DEBUG: Metadata rows from DB:", self.metadata_list)

            self.meta_input.clear()
            self.meta_input.addItem("Select metadata", -1)  # placeholder
            if not self.metadata_list:
                print("DEBUG: No metadata found in DB!")
            else:
                for meta_id, meta_name, meta_desc in self.metadata_list:
                    print(f"DEBUG: Adding metadata -> ID: {meta_id}, Name: {meta_name}")
                    self.meta_input.addItem(meta_name, meta_id)

            self.meta_input.setCurrentIndex(0)

        except Exception as e:
            print("Error loading metadata:", e)

    def refresh_table(self):
        """Load ingredients into the table."""
        try:
            self.data = IngredientDB.get_ingredients()
            print("DEBUG: Ingredients loaded:", self.data)

            self.table.setRowCount(0)
            if not self.data:
                return

            self.table.setRowCount(len(self.data))
            for row, ing in enumerate(self.data):
                self.table.setItem(row, 0, QtWidgets.QTableWidgetItem(str(ing.get("ID", ""))))
                self.table.setItem(row, 1, QtWidgets.QTableWidgetItem(str(ing.get("Name", ""))))
                self.table.setItem(row, 2, QtWidgets.QTableWidgetItem(str(ing.get("Size", ""))))
                self.table.setItem(row, 3, QtWidgets.QTableWidgetItem(str(ing.get("Unit", ""))))

                # Lookup metadata safely
                meta_name = "Unknown"
                meta_id = ing.get("MetadataID", None)
                if meta_id is not None:
                    for m in self.metadata_list:
                        if m[0] == meta_id:
                            meta_name = m[1]
                            break
                self.table.setItem(row, 4, QtWidgets.QTableWidgetItem(meta_name))

        except Exception as e:
            print("Error refreshing table:", e)

    def add_ingredient(self):
        name = self.name_input.text().strip()
        unit = self.unit_input.text().strip()
        size_text = self.size_input.text().strip()
        meta_index = self.meta_input.currentIndex()
        meta_id = self.meta_input.itemData(meta_index)

        if not name or not unit:
            QtWidgets.QMessageBox.warning(self, "Error", "Name and Unit cannot be empty")
            return

        try:
            size = float(size_text)
        except ValueError:
            QtWidgets.QMessageBox.warning(self, "Error", "Size must be a number")
            return

        if meta_id == -1:
            QtWidgets.QMessageBox.warning(self, "Error", "Please select a metadata tag")
            return

        try:
            IngredientDB.add_ingredient(name, size, unit, meta_id)
            self.refresh_table()
            self.clear_form()
        except Exception as e:
            print("Error adding ingredient:", e)

    def update_ingredient(self):
        selected = self.table.currentRow()
        if selected < 0:
            return
        ing_id = self.data[selected]["ID"]
        name = self.name_input.text().strip()
        unit = self.unit_input.text().strip()
        size_text = self.size_input.text().strip()
        meta_index = self.meta_input.currentIndex()
        meta_id = self.meta_input.itemData(meta_index)

        if not name or not unit:
            QtWidgets.QMessageBox.warning(self, "Error", "Name and Unit cannot be empty")
            return

        try:
            size = float(size_text)
        except ValueError:
            QtWidgets.QMessageBox.warning(self, "Error", "Size must be a number")
            return

        try:
            IngredientDB.update_ingredient(ing_id, name, size, unit, meta_id)
            self.refresh_table()
            self.clear_form()
        except Exception as e:
            print("Error updating ingredient:", e)

    def delete_ingredient(self):
        selected = self.table.currentRow()
        if selected < 0:
            return
        ing_id = self.data[selected]["ID"]
        try:
            IngredientDB.delete_ingredient(ing_id)
            self.refresh_table()
            self.clear_form()
        except Exception as e:
            print("Error deleting ingredient:", e)

    def fill_form(self, row, column):
        ing = self.data[row]
        self.name_input.setText(str(ing.get("Name", "")))
        self.size_input.setText(str(ing.get("Size", "")))
        self.unit_input.setText(str(ing.get("Unit", "")))

        # Select metadata safely
        meta_id = ing.get("MetadataID", -1)
        index = self.meta_input.findData(meta_id)
        if index >= 0:
            self.meta_input.setCurrentIndex(index)
        else:
            self.meta_input.setCurrentIndex(0)

    def clear_form(self):
        self.name_input.clear()
        self.size_input.clear()
        self.unit_input.clear()
        self.meta_input.setCurrentIndex(0)
