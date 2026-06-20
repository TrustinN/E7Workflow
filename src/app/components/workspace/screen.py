from PyQt5.QtWidgets import QPushButton, QVBoxLayout, QWidget


class WorkspaceScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)

        self.btn = QPushButton("Add Workspace")
        self.layout.addWidget(self.btn)
        self.layout.addStretch()
