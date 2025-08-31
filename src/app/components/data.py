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

    def setData(self, data: WorkspaceData):
        self.widget.clear()

        workspaceLabel = "Workspace: "
        if data.workspace is not None:
            workspaceLabel += data.workspace.name
        else:
            workspaceLabel += "None"
        self.widget.addItem(workspaceLabel)

        actionLabel = "Action: "
        if data.action is not None:
            actionLabel += data.action.__name__
        else:
            actionLabel += "None"
        self.widget.addItem(actionLabel)

        edgesLabel = "Edges: "
        if data.edges is not None:
            edgesLabel += str(data.edges)
        else:
            edgesLabel += "None"
        self.widget.addItem(edgesLabel)
