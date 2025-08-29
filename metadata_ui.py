from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QInputDialog, QMessageBox
from metadata_db import MetadataDB

class MetadataPopup(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Metadata Tags Manager")
        self.resize(700, 400)

        # --- Data ---
        self.data = []

        # --- Table ---
        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Name", "Description", "Unit"])
        self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

        # --- Buttons ---
        btn_layout = QtWidgets.QHBoxLayout()
        self.add_btn = QtWidgets.QPushButton("Add")
        self.edit_btn = QtWidgets.QPushButton("Edit")
        self.delete_btn = QtWidgets.QPushButton("Delete")
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.edit_btn)
        btn_layout.addWidget(self.delete_btn)

        # --- Layout ---
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addLayout(btn_layout)
        main_layout.addWidget(self.table)

        # --- Connect Buttons ---
        self.add_btn.clicked.connect(self.add_metadata)
        self.edit_btn.clicked.connect(self.edit_metadata)
        self.delete_btn.clicked.connect(self.delete_metadata)

        # --- Load Table ---
        self.refresh_table()

    def refresh_table(self):
        self.data = MetadataDB.get_all_metadata()
        self.table.setRowCount(0)
        for m in self.data:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QtWidgets.QTableWidgetItem(str(m[0])))  # ID
            self.table.setItem(row, 1, QtWidgets.QTableWidgetItem(m[1]))       # Name
            self.table.setItem(row, 2, QtWidgets.QTableWidgetItem(m[2] or "")) # Description
            self.table.setItem(row, 3, QtWidgets.QTableWidgetItem(m[3] or "")) # Unit

    def add_metadata(self):
        name, ok1 = QInputDialog.getText(self, "Add Metadata", "Tag name:")
        if not ok1 or not name.strip():
            return
        desc, ok2 = QInputDialog.getText(self, "Add Metadata", "Description (optional):")
        if not ok2:
            return
        unit, ok3 = QInputDialog.getText(self, "Add Metadata", "Unit (e.g. g, ml, pcs):")
        if ok3 and unit.strip():
            MetadataDB.add_metadata(name.strip(), desc.strip() if desc else "", unit.strip())
            self.refresh_table()

    def edit_metadata(self):
        selected = self.table.currentRow()
        if selected < 0:
            return
        metadata_id = self.data[selected][0]
        current_name = self.data[selected][1]
        current_desc = self.data[selected][2] or ""
        current_unit = self.data[selected][3] or ""

        name, ok1 = QInputDialog.getText(self, "Edit Metadata", "Tag name:", text=current_name)
        if not ok1 or not name.strip():
            return
        desc, ok2 = QInputDialog.getText(self, "Edit Metadata", "Description (optional):", text=current_desc)
        if not ok2:
            return
        unit, ok3 = QInputDialog.getText(self, "Edit Metadata", "Unit (e.g. g, ml, pcs):", text=current_unit)
        if ok3 and unit.strip():
            MetadataDB.update_metadata(metadata_id, name.strip(), desc.strip() if desc else "", unit.strip())
            self.refresh_table()

    def delete_metadata(self):
        selected = self.table.currentRow()
        if selected < 0:
            return
        metadata_id = self.data[selected][0]
        confirm = QMessageBox.question(
            self, "Confirm Delete", "Are you sure you want to delete this metadata tag?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            MetadataDB.delete_metadata(metadata_id)
            self.refresh_table()