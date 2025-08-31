from PyQt5.QtWidgets import QListWidget, QVBoxLayout, QWidget


class WorkspaceData:
    def __init__(self):
        self.workspace = None
        self.action = None
        self.edges = None


class DataWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.setFixedSize(400, 300)
        self.widget = QListWidget()
        self.layout.addWidget(self.widget)

        self.data = None

    def setData(self, data: WorkspaceData):
        self.data = data
        self.renderData()

    def renderData(self):
        self.widget.clear()

        if self.data:
            self.widget.addItem(f"Workspace: {self.data.workspace.name}")
            self.widget.addItem(f"Action: {self.data.action.__name__}")
            self.widget.addItem(f"Edges: {self.data.edges}")
