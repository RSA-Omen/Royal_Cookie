from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QInputDialog, QMessageBox
from metadata_logic import MetadataLogic

class MetadataPopup(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Metadata Tags Manager")
        self.resize(700, 400)

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
        self.data = MetadataLogic.get_all_metadata()
        self.table.setRowCount(0)
        for m in self.data:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QtWidgets.QTableWidgetItem(str(m["ID"])))
            self.table.setItem(row, 1, QtWidgets.QTableWidgetItem(m["Name"]))
            self.table.setItem(row, 2, QtWidgets.QTableWidgetItem(m["Description"] or ""))
            self.table.setItem(row, 3, QtWidgets.QTableWidgetItem(m["Unit"] or ""))

    def add_metadata(self):
        name, ok1 = QInputDialog.getText(self, "Add Metadata", "Tag name:")
        if not ok1 or not name.strip():
            return
        desc, ok2 = QInputDialog.getText(self, "Add Metadata", "Description (optional):")
        if not ok2:
            return
        unit, ok3 = QInputDialog.getText(self, "Add Metadata", "Unit (e.g. g, ml, pcs):")
        if ok3 and unit.strip():
            MetadataLogic.add_metadata(name.strip(), desc.strip() if desc else "", unit.strip())
            self.refresh_table()

    def edit_metadata(self):
        selected = self.table.currentRow()
        if selected < 0:
            return
        metadata = self.data[selected]
        name, ok1 = QInputDialog.getText(self, "Edit Metadata", "Tag name:", text=metadata["Name"])
        if not ok1 or not name.strip():
            return
        desc, ok2 = QInputDialog.getText(self, "Edit Metadata", "Description (optional):", text=metadata["Description"] or "")
        if not ok2:
            return
        unit, ok3 = QInputDialog.getText(self, "Edit Metadata", "Unit (e.g. g, ml, pcs):", text=metadata["Unit"] or "")
        if ok3 and unit.strip():
            MetadataLogic.update_metadata(metadata["ID"], name.strip(), desc.strip() if desc else "", unit.strip())
            self.refresh_table()

    def delete_metadata(self):
        selected = self.table.currentRow()
        if selected < 0:
            return
        metadata = self.data[selected]
        confirm = QMessageBox.question(
            self, "Confirm Delete", "Are you sure you want to delete this metadata tag?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            MetadataLogic.delete_metadata(metadata["ID"])
            self.refresh_table()