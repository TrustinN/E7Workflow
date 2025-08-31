from PyQt5.QtWidgets import QListWidget, QVBoxLayout, QWidget

from ..workspace.workspace import extractGeometry


class WorkspaceData:
    def __init__(self):
        self.workspace = None
        self.action = None
        self.edges = None
        self.defaultChildEntryNodeID = None
        self.node = None
        self.scene = None
        self.childData: list[WorkspaceData] = []

    def serialize(self):
        wks = self.workspace
        data = {
            "edges": self.edges,
            "geometry": extractGeometry(wks),
            "ID": wks.id,
            "name": wks.name,
            "parentID": wks.parentID,
            "padding": wks.padding,
            "childData": [data.serialize() for data in self.childData],
        }
        if self.node:
            nodePos = self.node.pos()
            data["nodeGeometry"] = [nodePos.x(), nodePos.y()]

        if self.action:
            data["action"] = self.action.__name__

        return data


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
