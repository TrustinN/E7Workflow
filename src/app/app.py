from PyQt5.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ..io.io import Serializer
from .components.editor import EditorWidget
from .components.manager import WorkspaceManager
from .state.state import StateWidget
from .workspace.workspace import layoutToBBox


class RunnerWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.state = {}
        self.stateView = StateWidget()
        self.stateView.renderState(self.state)

        self.layout.addWidget(self.stateView)


class App(QApplication):
    def __init__(self):
        super().__init__([])

        self.window = QMainWindow()
        self.widget = QWidget()
        self.layout = QHBoxLayout()
        self.widget.setLayout(self.layout)
        self.window.setCentralWidget(self.widget)
        self.window.show()

        self.editor = EditorWidget()
        self.manager = WorkspaceManager()
        self.runner = RunnerWidget()
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
        self.layout.addWidget(self.runner)
        self.layout.addWidget(self.importBtn)
        self.layout.addWidget(self.exportBtn)

        self.editor.workspaceCreated_.connect(self.manager.registerWorkspace)
        self.manager.workspaceRegistered.connect(
            lambda id: self.editor.addNode(
                self.manager.scene(self.manager.parentID(id)),
                id,
                self.manager.workspace(id).name,
            )
        )
        self.manager.activeChanged.connect(
            lambda id: self.editor.graphView.setScene(self.manager.scene(id))
        )
        self.editor.graphEditorActions.addEdge_.connect(
            lambda: self.editor.addEdge(self.manager.activeScene)
        )

        self.importBtn.clicked.connect(self.importConfig)
        self.exportBtn.clicked.connect(self.exportConfig)

        self.initState()

    def initState(self):
        self.manager.initState()

    def reset(self):
        self.manager.reset()

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
