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

from .constants import CONFIG_DIR, ROOT_ID
from .graph.editor import GraphEditor, GraphEditorActions, InteractiveGraphScene
from .workspace.editor import WorkspacEditorActions, WorkspaceEditor
from .workspace.helpers import click, screenshot, scroll
from .workspace.workspace import (
    Workspace,
    applyGeometry,
    exportData,
    extractGeometry,
    importData,
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
        "desc": "Drags the moues from one edge to the opposite edge given a scroll direction",
    },
]


class App(QApplication):
    def __init__(self):
        super().__init__([])

        self.window = QMainWindow()
        self.widget = QWidget()
        self.layout = QVBoxLayout()
        self.widget.setLayout(self.layout)
        self.window.setCentralWidget(self.widget)
        self.window.show()

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

        self.importBtn = QPushButton("Import")
        self.exportBtn = QPushButton("Export")

        self.layout.addWidget(self.wksEditorActions)
        self.layout.addWidget(self.graphEditorActions)
        self.layout.addWidget(self.graphView)
        self.layout.addWidget(self.importBtn)
        self.layout.addWidget(self.exportBtn)
        self.layout.addWidget(self.wksEditor)
        self.layout.addWidget(self.graphEditor)

        self.importBtn.clicked.connect(self.importConfig)
        self.exportBtn.clicked.connect(self.exportConfig)

        self.setup()

    def setup(self):
        self.wksHandler[ROOT_ID] = Workspace(ROOT_ID, "Root")
        self.sceneHandler[ROOT_ID] = InteractiveGraphScene()

        self.activeWks = self.wksHandler[ROOT_ID]
        self.activeScene = self.sceneHandler[ROOT_ID]
        self.graphView.setScene(self.activeScene)

        self.activeWks.show()
        self.activeWks.unlock()
        self.activeWks.setPadding(15)
        self.activeWks.mousePress.connect(lambda: self.onSceneChange(ROOT_ID))

        self.wksEditorActions.add_.connect(self.addWorkspace)
        self.graphEditorActions.addEdge_.connect(self.addEdge)

    def addWorkspace(self):
        wks = self.wksEditor.addWorkspace()
        self.activeWks.addChild(wks)

        self.wksHandler[wks.id] = wks
        self.sceneHandler[wks.id] = InteractiveGraphScene()

        self.graphEditor.addNode(self.activeScene, wks.id)
        node = self.activeScene.node(wks.id)
        node.setDisplayText(wks.name)

        wks.mousePress.connect(lambda: self.onSceneChange(wks.id))
        node.emitter.onMousePress_.connect(
            lambda: self.onSelectionChanged(self.activeWks.id, wks.id)
        )

    def addEdge(self):
        self.graphEditor.addEdge(self.activeScene)

    def reset(self):
        pass

    def importConfig(self):
        pass

    def exportConfig(self):
        pass

    def onWorkspaceFocus(self, id):
        pass

    def onSceneChange(self, id):
        self.activeScene = self.sceneHandler[id]
        self.activeWks = self.wksHandler[id]

        self.graphView.setScene(self.activeScene)

    def onSelectionChanged(self, prevId, nextId):
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

        self.activeWks = self.wksHandler[nextId]
