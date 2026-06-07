from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QInputDialog, QLineEdit, QPushButton, QVBoxLayout, QWidget


class WorkspaceButtons(QWidget):
    createWorkspace_ = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.createBtn = QPushButton("Create Workspace")
        self.exportBtn = QPushButton("Export Workspace")
        self.importBtn = QPushButton("Import Workspace")

        self.createBtn.clicked.connect(self.onWorkspaceCreate)

        self.layout.addWidget(self.createBtn)
        self.layout.addWidget(self.exportBtn)
        self.layout.addWidget(self.importBtn)

    def onWorkspaceCreate(self):
        name, ok = QInputDialog.getText(
            self,
            "QInputDialog.getText()",
            "Workspace Name:",
            QLineEdit.Normal,
            "WS Name",
        )
        if name and ok:
            self.createWorkspace_.emit(name)
