from PyQt5 import QtWidgets
from ingredient_logic import IngredientLogic
from metadata_logic import MetadataLogic

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
        self.meta_input = QtWidgets.QComboBox()
        form_layout.addWidget(self.name_input)
        form_layout.addWidget(self.size_input)
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
        self.metadata_list = MetadataLogic.get_all_metadata()
        self.meta_input.clear()
        self.meta_input.addItem("Select metadata", -1)
        for meta in self.metadata_list:
            self.meta_input.addItem(meta["Name"], meta["ID"])
        self.meta_input.setCurrentIndex(0)

    def refresh_table(self):
        self.data = IngredientLogic.get_ingredients()
        self.table.setRowCount(0)
        for ing in self.data:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QtWidgets.QTableWidgetItem(str(ing["ID"])))
            self.table.setItem(row, 1, QtWidgets.QTableWidgetItem(ing["Name"]))
            self.table.setItem(row, 2, QtWidgets.QTableWidgetItem(str(ing["Size"])))
            # Lookup unit from metadata
            meta = next((m for m in self.metadata_list if m["ID"] == ing["MetadataID"]), None)
            unit = meta["Unit"] if meta else ""
            self.table.setItem(row, 3, QtWidgets.QTableWidgetItem(unit))
            meta_name = meta["Name"] if meta else "Unknown"
            self.table.setItem(row, 4, QtWidgets.QTableWidgetItem(meta_name))

    def add_ingredient(self):
        name = self.name_input.text().strip()
        size_text = self.size_input.text().strip()
        meta_index = self.meta_input.currentIndex()
        meta_id = self.meta_input.itemData(meta_index)
        if not name:
            QtWidgets.QMessageBox.warning(self, "Error", "Name cannot be empty")
            return
        try:
            size = float(size_text)
        except ValueError:
            QtWidgets.QMessageBox.warning(self, "Error", "Size must be a number")
            return
        if meta_id == -1:
            QtWidgets.QMessageBox.warning(self, "Error", "Please select a metadata tag")
            return
        IngredientLogic.add_ingredient(name, size, meta_id)
        self.refresh_table()
        self.clear_form()

    def update_ingredient(self):
        selected = self.table.currentRow()
        if selected < 0:
            return
        ing_id = self.data[selected]["ID"]
        name = self.name_input.text().strip()
        size_text = self.size_input.text().strip()
        meta_index = self.meta_input.currentIndex()
        meta_id = self.meta_input.itemData(meta_index)
        if not name:
            QtWidgets.QMessageBox.warning(self, "Error", "Name cannot be empty")
            return
        try:
            size = float(size_text)
        except ValueError:
            QtWidgets.QMessageBox.warning(self, "Error", "Size must be a number")
            return
        IngredientLogic.update_ingredient(ing_id, name, size, meta_id)
        self.refresh_table()
        self.clear_form()

    def delete_ingredient(self):
        selected = self.table.currentRow()
        if selected < 0:
            return
        ing_id = self.data[selected]["ID"]
        IngredientLogic.delete_ingredient(ing_id)
        self.refresh_table()
        self.clear_form()

    def fill_form(self, row, column):
        ing = self.data[row]
        self.name_input.setText(ing["Name"])
        self.size_input.setText(str(ing["Size"]))
        meta_id = ing["MetadataID"]
        index = self.meta_input.findData(meta_id)
        self.meta_input.setCurrentIndex(index if index >= 0 else 0)

    def clear_form(self):
        self.name_input.clear()
        self.size_input.clear()
        self.meta_input.setCurrentIndex(0)