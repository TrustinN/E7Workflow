from PyQt5.QtWidgets import QInputDialog, QLineEdit, QPushButton, QVBoxLayout, QWidget


class WorkspaceWidget(QWidget):

    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.createBtn = QPushButton("Create Workspace")
        self.exportBtn = QPushButton("Export Workspace")
        self.importBtn = QPushButton("Import Workspace")

        self.layout.addWidget(self.createBtn)
        self.layout.addWidget(self.exportBtn)
        self.layout.addWidget(self.importBtn)

    def getWorkspaceName(self):
        name, ok = QInputDialog.getText(
            self,
            "QInputDialog.getText()",
            "Workspace Name:",
            QLineEdit.Normal,
            "WS Name",
        )
        return name
