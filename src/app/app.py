import json
import os

from PyQt5.QtCore import QObject, Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QApplication,
    QGraphicsView,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ..io.io import LogEntry, Serializer
from .constants import CONFIG_DIR, ROOT_ID
from .graph.editor import GraphEditor, GraphEditorActions, InteractiveGraphScene
from .state.state import StateWidget
from .workspace.editor import WorkspacEditorActions, WorkspaceEditor
from .workspace.helpers import click, screenshot, scroll
from .workspace.workspace import (
    Workspace,
    applyGeometry,
    exportData,
    extractGeometry,
    importData,
    layoutToBBox,
    listToQPoint,
    qpointToList,
)

actions = [
    {
        "name": click.__name__,
        "desc": "Clicks the center of the workspace",
        "action": click,
    },
    {
        "name": screenshot.__name__,
        "desc": "Takes a screenshot given the borders of the workspace",
        "action": screenshot,
    },
    {
        "name": scroll.__name__,
        "action": scroll,
        "desc": "Drags the mouse from one edge to the opposite edge given a scroll direction",
    },
]


class EditorWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.wksEditor: WorkspaceEditor = WorkspaceEditor()
        self.wksEditorActions: WorkspacEditorActions = WorkspacEditorActions()
        self.wksHandler: dict[any, Workspace] = {}

        self.graphEditor: GraphEditor = GraphEditor()
        self.graphEditorActions: GraphEditorActions = GraphEditorActions()
        self.sceneHandler: dict[any, InteractiveGraphScene] = {}

        self.graphView = QGraphicsView()
        self.graphView.setFixedSize(400, 300)
        self.graphView.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.graphView.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.layout.addWidget(self.wksEditorActions)
        self.layout.addWidget(self.graphEditorActions)
        self.layout.addWidget(self.graphView)
        self.layout.addWidget(self.wksEditor)
        self.layout.addWidget(self.graphEditor)

    def setup(self):
        self.wksHandler[ROOT_ID] = Workspace(ROOT_ID, "Root")
        self.sceneHandler[ROOT_ID] = InteractiveGraphScene()

        self.activeWks = self.wksHandler[ROOT_ID]
        self.activeScene = self.sceneHandler[ROOT_ID]
        self.graphView.setScene(self.activeScene)

        self.activeWks.show()
        self.activeWks.unlock()
        self.activeWks.setPadding(15)
        self.activeWks.mousePress.connect(lambda: self.changeScene(ROOT_ID))

        self.wksEditorActions.add_.connect(self.addWorkspace)
        self.graphEditorActions.addEdge_.connect(self.addEdge)

    def addWorkspace(self, id=None, name=None):
        wks = self.wksEditor.addWorkspace(id, name)
        self.activeWks.addChild(wks)

        self.wksHandler[wks.id] = wks
        self.sceneHandler[wks.id] = InteractiveGraphScene()

        self.graphEditor.addNode(self.activeScene, wks.id)
        node = self.activeScene.node(wks.id)
        node.setDisplayText(wks.name)

        wks.mousePress.connect(lambda: self.changeScene(wks.id))
        node.emitter.onMousePress_.connect(lambda: self.changeWorkspace(wks.id))

    def addEdge(self):
        self.graphEditor.addEdge(self.activeScene)

    def reset(self):
        rootWks = self.wksHandler[ROOT_ID]
        rootWks.deleteLater()

        self.wksHandler.clear()
        self.sceneHandler.clear()

        self.activeWks = None
        self.activeScene = None
        self.graphView.setScene(None)

        self.setup()

    def changeScene(self, id):
        self.activeScene = self.sceneHandler[id]
        self.activeWks = self.wksHandler[id]

        self.graphView.setScene(self.activeScene)

    def changeWorkspace(self, id):
        prevId = self.activeWks.id
        nextId = id
        if prevId == nextId:
            return

        if prevId != ROOT_ID:
            wks = self.wksHandler[prevId]
            if wks:
                wks.hide()
                wks.lock()

        if nextId != ROOT_ID:
            wks = self.wksHandler[nextId]
            if wks:
                wks.show()
                wks.unlock()

        self.activeScene.setActiveNode(self.activeScene.node(id))

    def getWorkspaceSnapshot(self, workspace: Workspace):
        scene = self.sceneHandler[workspace.parentID]
        return {
            "edges": scene.tuples[workspace.id],
            "geometry": extractGeometry(workspace),
            "ID": workspace.id,
            "name": workspace.name,
            "parentID": workspace.parentID,
        }

    def snapshot(self, serializer: Serializer):
        snapshots = []

        def getData(workspace: Workspace):
            for wks in workspace.wkspaces:
                snapshots.append(self.getWorkspaceSnapshot(wks))
                getData(wks)

        rootWks = self.wksHandler[ROOT_ID]
        getData(rootWks)

        for data in snapshots:
            serializer.addLog("restoreWorkspace", data)

        for data in snapshots:
            serializer.addLog("restoreEdges", data)


class RunnerWidget(QWidget):
    def __init__(self):
        super().__init__()


class App(QApplication):
    def __init__(self):
        super().__init__([])

        self.window = QMainWindow()
        self.widget = QWidget()
        self.layout = QVBoxLayout()
        self.widget.setLayout(self.layout)
        self.window.setCentralWidget(self.widget)
        self.window.show()

        self.editor = EditorWidget()
        self.serializer = Serializer(
            self,
            {
                "restoreWorkspace": restoreWorkspace,
                "restoreEdges": restoreEdges,
            },
        )

        self.importBtn = QPushButton("Import")
        self.importBtn.clicked.connect(self.importConfig)

        self.exportBtn = QPushButton("Export")
        self.exportBtn.clicked.connect(self.exportConfig)

        self.layout.addWidget(self.editor)
        self.layout.addWidget(self.importBtn)
        self.layout.addWidget(self.exportBtn)

        self.setup()

    def setup(self):
        self.editor.setup()

    def reset(self):
        self.editor.reset()

    def importConfig(self):
        self.reset()
        self.applySnapshot()

    def exportConfig(self):
        self.serializer.reset()
        self.editor.snapshot(self.serializer)
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

    app.editor.changeScene(parentID)
    app.editor.addWorkspace(id, name)

    wks = app.editor.wksHandler[id]
    wks.setGeometry(layoutToBBox(geometry))


def restoreEdges(app: App, **kwargs):
    parentID = kwargs["parentID"]
    id = kwargs["ID"]
    edges: list[any] = kwargs["edges"]

    app.editor.changeScene(parentID)
    scene = app.editor.sceneHandler[parentID]
    for id2 in edges:
        scene.newSceneArrow(id, id2)
