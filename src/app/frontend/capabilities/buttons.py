from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QInputDialog, QLineEdit, QPushButton, QVBoxLayout, QWidget


class Buttons(QWidget):
    createWorkspace_ = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.createBtn = QPushButton("Create Workspace")
        self.setE1Btn = QPushButton("SetEdgeStart")
        self.setE2Btn = QPushButton("SetEdgeEnd")
        self.createEdgeBtn = QPushButton("Create Edge")
        self.entryBtn = QPushButton("Set Entry")
        self.executeBtn = QPushButton("Execute")

        self.exportBtn = QPushButton("Export")
        self.importBtn = QPushButton("Import")

        self.createBtn.clicked.connect(self.onWorkspaceCreate)

        self.layout.addWidget(self.createBtn)
        self.layout.addWidget(self.setE1Btn)
        self.layout.addWidget(self.setE2Btn)
        self.layout.addWidget(self.createEdgeBtn)
        self.layout.addWidget(self.entryBtn)
        self.layout.addWidget(self.executeBtn)

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
