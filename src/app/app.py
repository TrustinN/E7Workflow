from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ..io.io import Serializer
from .components.data import DataWidget
from .components.editor import EditorWidget
from .components.manager import WorkspaceManager
from .components.runner import RunnerWidget
from .graph.graph import NODE_HIGHLIGHT_COLOR
from .workspace.helpers import actions
from .workspace.workspace import WORKSPACE_TRANSPARENCY, layoutToBBox


class App(QApplication):
    def __init__(self):
        super().__init__([])

        self.window = QMainWindow()
        self.widget = QWidget()
        self.layout = QHBoxLayout()
        self.col2Layout = QVBoxLayout()
        self.widget.setLayout(self.layout)
        self.window.setCentralWidget(self.widget)
        self.window.show()

        self.editor = EditorWidget()
        self.manager = WorkspaceManager()
        self.runner = RunnerWidget(self.manager.sendData_)
        self.dataDisplay = DataWidget()
        self.serializer = Serializer(
            self,
            {
                "restoreWorkspace": restoreWorkspace,
                "restoreEdges": restoreEdges,
            },
        )

        self.importBtn = QPushButton("Import")
        self.exportBtn = QPushButton("Export")

        self.layout.addWidget(self.editor)
        self.col2Layout.addWidget(self.dataDisplay)
        self.col2Layout.addWidget(self.runner)
        self.layout.addLayout(self.col2Layout)
        self.layout.addWidget(self.importBtn)
        self.layout.addWidget(self.exportBtn)

        self.initSignals()
        self.initState()

    def initSignals(self):
        self.editor.workspaceCreated_.connect(self.manager.registerWorkspace)

        # Add graphics node to graph view
        self.manager.workspaceRegistered.connect(self.onWorkspaceRegistered)

        # Change InteractiveGraphicsScene on active workspace change
        self.manager.activeChanged.connect(
            lambda id: self.editor.graphView.setScene(self.manager.scene(id))
        )

        # Add edge to scene on button press
        self.editor.graphEditorActions.addEdge_.connect(
            lambda: self.editor.addEdge(self.manager.activeScene)
        )

        # Update action of focused workspace
        self.editor.actions.currentTextChanged.connect(self.manager.setAction)

        # Poll data from manager
        self.runner.resolver.getData_.connect(self.manager.sendData)

        self.importBtn.clicked.connect(self.importConfig)
        self.exportBtn.clicked.connect(self.exportConfig)

    def initState(self):
        self.editor.setActions(actions)
        self.manager.initState()

    def reset(self):
        self.manager.reset()

    def onWorkspaceRegistered(self, id):
        wks = self.manager.workspace(id)
        data = self.manager.data(id)
        node = self.editor.addNode(
            self.manager.scene(self.manager.parentID(id)),
            id,
            wks.name,
        )

        wks.mousePress.connect(lambda: self.dataDisplay.setData(data))
        node.emitter.onMousePress_.connect(lambda: self.dataDisplay.setData(data))
        highlightColor = QColor(NODE_HIGHLIGHT_COLOR)
        highlightColor.setAlpha(WORKSPACE_TRANSPARENCY)
        node.emitter.onMousePress_.connect(lambda: wks.setColor(highlightColor))

    def importConfig(self):
        self.reset()
        self.applySnapshot()

    def exportConfig(self):
        self.serializer.reset()
        self.manager.snapshot(self.serializer)
        self.serializer.writeData("snapshot")

    def applySnapshot(self):
        self.serializer.reset()
        self.serializer.readData("snapshot")
        self.serializer.playLogs()


def restoreWorkspace(app: App, **kwargs):
    geometry = kwargs["geometry"]
    id = kwargs["ID"]
    name = kwargs["name"]
    parentID = kwargs["parentID"]
    nodeGeometry = kwargs["nodeGeometry"]

    app.manager.setActiveWorkspace(parentID)
    app.editor.addWorkspace(id, name)

    wks = app.manager.workspace(id)
    wks.setGeometry(layoutToBBox(geometry))

    app.manager.activeScene.node(id).setPos(*nodeGeometry)


def restoreEdges(app: App, **kwargs):
    parentID = kwargs["parentID"]
    id = kwargs["ID"]
    edges: list[any] = kwargs["edges"]

    app.manager.setActiveWorkspace(parentID)
    scene = app.manager.scene(parentID)
    for id2 in edges:
        scene.newSceneArrow(id, id2)
