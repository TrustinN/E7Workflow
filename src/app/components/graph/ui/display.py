import json
import os

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGraphicsView, QVBoxLayout, QWidget

from src.app.components.graph.model import GraphDocument, GraphModel, GraphViewState
from src.app.state import Context

from .controllers import FullViewController, MiniViewController
from .scene import GraphScene
from .viewmodel import GraphViewModel


class GraphViewport:
    def __init__(
        self,
        context: Context,
        model: GraphModel,
        viewState: GraphViewState,
        controllerType,
    ):
        self.scene = GraphScene()
        self.scene.setSceneRect(0, 0, 450, 275)

        self.controller = controllerType(
            context,
            self.scene,
            model,
            viewState,
        )

        self.viewModel = GraphViewModel(
            self.scene,
            model,
            viewState,
        )

        self.view = QGraphicsView(self.scene)
        self.view.setFixedSize(450, 275)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)


class GraphDisplay(QWidget):

    def __init__(self, context: Context, model: GraphModel):
        super().__init__()

        self.layout = QVBoxLayout(self)
        self.document = GraphDocument(model)

        self.miniViewState = GraphViewState()
        self.fullViewState = GraphViewState()

        self.document.addViewState("miniView", self.miniViewState)
        self.document.addViewState("fullView", self.fullViewState)

        self.mini = GraphViewport(
            context,
            model,
            self.miniViewState,
            MiniViewController,
        )

        self.full = GraphViewport(
            context,
            model,
            self.fullViewState,
            FullViewController,
        )

        self.layout.addWidget(self.mini.view)
        self.layout.addWidget(self.full.view)

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
