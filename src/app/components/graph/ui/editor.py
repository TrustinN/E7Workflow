import json
import os

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import (
    QGraphicsView,
    QHBoxLayout,
    QPushButton,
    QShortcut,
    QVBoxLayout,
    QWidget,
)

from src.app.components.graph.model import GraphDocument, GraphModel, GraphViewState
from src.app.state import Context, SelectionType

from .controllers import FullViewController, MiniViewController
from .scene import GraphScene
from .viewmodel import GraphViewModel


class GraphEditor(QWidget):
    requestEdge = pyqtSignal(str, str)

    def __init__(self, context: Context, model: GraphModel):
        super().__init__()

        self.context = context
        self.layout = QVBoxLayout(self)
        self.document = GraphDocument(model)

        self.miniViewState = GraphViewState()
        self.fullViewState = GraphViewState()

        self.document.addViewState("miniView", self.miniViewState)
        self.document.addViewState("fullView", self.fullViewState)

        self.miniScene = GraphScene()
        self.miniScene.setSceneRect(0, 0, 450, 275)
        self.miniController = MiniViewController(
            context, self.miniScene, model, self.miniViewState
        )
        self.miniViewModel = GraphViewModel(self.miniScene, model, self.miniViewState)
        self.miniView = QGraphicsView(self.miniScene)
        self.miniView.setFixedSize(450, 275)
        self.miniView.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.miniView.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.fullScene = GraphScene()
        self.fullScene.setSceneRect(0, 0, 450, 275)
        self.fullController = FullViewController(
            context, self.fullScene, model, self.fullViewState
        )
        self.fullViewModel = GraphViewModel(self.fullScene, model, self.fullViewState)
        self.fullView = QGraphicsView(self.fullScene)
        self.fullView.setFixedSize(450, 275)
        self.fullView.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.fullView.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.buttons = QWidget()
        self.btnLayout = QHBoxLayout(self.buttons)

        self.e1Shortcut = QShortcut("1", self)
        key = self.e1Shortcut.key().toString(QKeySequence.NativeText)
        self.e1Btn = QPushButton(f"Set Edge Start ({key})")
        self.e1Shortcut.activated.connect(self.setE1)
        self.e1Btn.clicked.connect(self.setE1)
        self.e1Shortcut.setContext(Qt.ApplicationShortcut)

        self.e2Shortcut = QShortcut("2", self)
        key = self.e2Shortcut.key().toString(QKeySequence.NativeText)
        self.e2Btn = QPushButton(f"Set Edge End ({key})")
        self.e2Shortcut.activated.connect(self.setE2)
        self.e2Btn.clicked.connect(self.setE2)
        self.e2Shortcut.setContext(Qt.ApplicationShortcut)

        self.edgeShortcut = QShortcut("E", self)
        key = self.edgeShortcut.key().toString(QKeySequence.NativeText)
        self.edgeBtn = QPushButton(f"Create Edge ({key})")
        self.edgeShortcut.activated.connect(self.setEdge)
        self.edgeBtn.clicked.connect(self.setEdge)
        self.edgeShortcut.setContext(Qt.ApplicationShortcut)

        self.btnLayout.addWidget(self.e1Btn)
        self.btnLayout.addWidget(self.e2Btn)
        self.btnLayout.addWidget(self.edgeBtn)

        self.e1 = None
        self.e2 = None

        self.layout.addWidget(self.buttons)
        self.layout.addWidget(self.miniView)
        self.layout.addWidget(self.fullView)

    def setE1(self):
        selection = self.context.selectionModel.getSelected()
        if selection.id and selection.type == SelectionType.WORKSPACE:
            self.e1 = selection.id

    def setE2(self):
        selection = self.context.selectionModel.getSelected()
        if selection.id and selection.type == SelectionType.WORKSPACE:
            self.e2 = selection.id

    def setEdge(self):
        if not (self.e1 and self.e2):
            return

        self.requestEdge.emit(self.e1, self.e2)
        self.e1 = None
        self.e2 = None

    def updateNode(self, id: str, patch: dict):
        self.miniViewState.updateNode(id, patch)
        self.fullViewState.updateNode(id, patch)

    def updateEdge(self, id: str, patch: dict):
        self.miniViewState.updateEdge(id, patch)
        self.fullViewState.updateEdge(id, patch)

    def saveState(self, path):
        miniSaveFile = os.path.join(path, "miniview.json")
        miniState = self.miniViewState.toData()
        with open(miniSaveFile, "w") as f:
            json.dump(miniState, f, indent=4)

        fullSaveFile = os.path.join(path, "fullview.json")
        fullState = self.fullViewState.toData()
        with open(fullSaveFile, "w") as f:
            json.dump(fullState, f, indent=4)

    def loadState(self, path):
        miniSaveFile = os.path.join(path, "miniview.json")
        miniState = None
        with open(miniSaveFile, "r") as f:
            miniState = json.load(f)
        self.miniViewState.fromData(miniState)

        fullSaveFile = os.path.join(path, "fullview.json")
        fullState = None
        with open(fullSaveFile, "r") as f:
            fullState = json.load(f)
        self.fullViewState.fromData(fullState)
