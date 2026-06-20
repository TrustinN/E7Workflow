import os

from PyQt5.QtWidgets import (
    QComboBox,
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)

from src.app.config import SAVE_DIR
from src.app.frontend.events import Node


class SerializationCapability(Node):
    def __init__(self):
        super().__init__()
        os.makedirs(SAVE_DIR, exist_ok=True)

    def requestReset(self):
        self.publish("/App/Reset")

    def requestExport(self, id):
        path = os.path.join(SAVE_DIR, id)
        os.makedirs(path, exist_ok=True)
        self.publish("/App/Export", {"path": path})

    def requestImport(self, id):
        path = os.path.join(SAVE_DIR, id)
        self.publish("/App/Import", {"path": path})

    def handleExport(self):
        dialog = QDialog()
        dialog.setWindowTitle("Export Config")
        dialog.setMinimumSize(350, 180)

        layout = QVBoxLayout(dialog)
        layout.addWidget(QLabel("Select existing or type new name:"))

        combo = QComboBox(dialog)
        combo.setEditable(True)
        combo.addItems(self.getAvailableConfigs())
        combo.setCompleter(None)
        combo.setEditText("Untitled")
        combo.lineEdit().selectAll()

        layout.addWidget(combo)
        btnRow = QHBoxLayout()

        exportBtn = QPushButton("Export", dialog)
        cancelBtn = QPushButton("Cancel", dialog)

        btnRow.addWidget(exportBtn)
        btnRow.addWidget(cancelBtn)

        layout.addLayout(btnRow)

        def accept():
            dialog.accept()

        def reject():
            dialog.reject()

        exportBtn.clicked.connect(accept)
        cancelBtn.clicked.connect(reject)

        if dialog.exec_():
            name = combo.currentText().strip()
            if name:
                self.requestExport(name)

    def handleImport(self):
        dialog = QDialog()
        dialog.setWindowTitle("Select Config")
        dialog.resize(300, 150)
        dialog.setMinimumSize(300, 150)

        layout = QVBoxLayout(dialog)

        combo = QComboBox(dialog)
        combo.addItems(self.getAvailableConfigs())

        layout.addWidget(combo)

        btn = QPushButton("Import", dialog)
        layout.addWidget(btn)

        def on_accept():
            dialog.accept()

        btn.clicked.connect(on_accept)

        if dialog.exec_():
            name = combo.currentText()
            self.requestReset()
            self.requestImport(name)

    def getAvailableConfigs(self):
        if not os.path.exists(SAVE_DIR):
            return []

        return [
            name
            for name in os.listdir(SAVE_DIR)
            if os.path.isdir(os.path.join(SAVE_DIR, name))
        ]
