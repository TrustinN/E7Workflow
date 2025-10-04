from PyQt5.QtWidgets import QInputDialog, QLineEdit, QPushButton, QVBoxLayout, QWidget


class WorkspaceWidget(QWidget):

    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.createWorkspaceBtn = QPushButton("Create Workspace")
        self.exportWorkspaceBtn = QPushButton("Export Workspace")
        self.restoreWorkspaceBtn = QPushButton("Restore Workspace")

        self.layout.addWidget(self.createWorkspaceBtn)
        self.layout.addWidget(self.exportWorkspaceBtn)
        self.layout.addWidget(self.restoreWorkspaceBtn)

    def getWorkspaceName(self):
        name, ok = QInputDialog.getText(
            self,
            "QInputDialog.getText()",
            "Workspace Name:",
            QLineEdit.Normal,
            "WS Name",
        )
        return name
