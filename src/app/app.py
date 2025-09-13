from dataclasses import dataclass

from nanoid import generate
from PyQt5.QtWidgets import QApplication, QHBoxLayout, QMainWindow, QPushButton, QWidget

from src.router.routing import Dispatcher

from .graph import GraphWidget
from .workspace import WorkspaceWidget


@dataclass
class Group:
    node: str | None = None
    workspace: str | None = None
    graph: str | None = None


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

    def closeEvent(self, event):
        QApplication.quit()


class App(QApplication):
    def __init__(self, dispatcher: Dispatcher):
        super().__init__([])

        self.window = MainWindow()
        self.widget = QWidget()
        self.layout = QHBoxLayout()
        self.widget.setLayout(self.layout)
        self.window.setCentralWidget(self.widget)
        self.window.show()

        self.graphWidget = GraphWidget(dispatcher)
        self.workspaceWidget = WorkspaceWidget(dispatcher)

        self.importBtn = QPushButton("Import")
        self.exportBtn = QPushButton("Export")

        self.nodes: dict[str, str] = {}
        self.graphs: dict[str, str] = {}
        self.workspaces: dict[str, str] = {}

        self.groups: dict[str, Group] = {}

        self.graphWidget.graphCreated_.connect(self.onGraphCreated)
        self.graphWidget.nodeCreated_.connect(self.onNodeCreated)

        self.workspaceWidget.workspaceCreated_.connect(self.onWorkspaceCreated)
        self.workspaceWidget.workspacePressed_.connect(self.onWorkspacePressed)

        self.layout.addWidget(self.graphWidget)
        self.layout.addWidget(self.workspaceWidget)

        self.initState()

    def initState(self):
        self.createGroup()
        self.graphWidget.createGraph()
        self.workspaceWidget.createWorkspace("Root")

    def createGroup(self):
        self.groupID = generate()
        self.groups[self.groupID] = Group()

    def onNodeCreated(self, id):
        self.createGroup()

        self.nodes[id] = self.groupID
        group = self.groups[self.groupID]
        group.node = id

        self.graphWidget.createGraph()
        self.workspaceWidget.createWorkspace()

    def onGraphCreated(self, id):
        self.graphs[id] = self.groupID
        group = self.groups[self.groupID]
        group.graph = id

        if not self.graphWidget.activeGraph:
            self.graphWidget.setActiveGraph(id)

    def onWorkspaceCreated(self, id):
        self.workspaces[id] = self.groupID
        group = self.groups[self.groupID]
        group.workspace = id

        parentID = self.workspaceWidget.focusedWorkspace()
        if not parentID:
            self.workspaceWidget.setFocusedWorkspace(id)
            self.workspaceWidget.updateWorkspace(id, {"userData": {"padding": 15}})

    def onWorkspacePressed(self, id):
        groupID = self.workspaces[id]
        group = self.groups[groupID]
        graphID = group.graph
        self.graphWidget.setActiveGraph(graphID)
