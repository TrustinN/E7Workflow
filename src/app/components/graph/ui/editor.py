from PyQt5.QtWidgets import QGraphicsView, QVBoxLayout, QWidget

from src.app.components.graph.model import GraphDocument, GraphModel, GraphViewState
from src.app.state import Context

from .controllers import FullViewController, MiniViewController
from .scene import GraphScene
from .viewmodel import GraphViewModel


class GraphEditor(QWidget):
    def __init__(self, context: Context, model: GraphModel):
        super().__init__()

        self.layout = QVBoxLayout(self)
        self.document = GraphDocument(model)

        self.miniViewState = GraphViewState()
        self.fullViewState = GraphViewState()

        self.document.addViewState("miniView", self.miniViewState)
        self.document.addViewState("fullView", self.fullViewState)

        self.miniScene = GraphScene()
        self.miniController = MiniViewController(context, self.miniScene, model)
        self.miniViewModel = GraphViewModel(self.miniScene, model, self.miniViewState)
        self.miniView = QGraphicsView(self.miniScene)

        self.fullScene = GraphScene()
        self.fullController = FullViewController(context, self.fullScene, model)
        self.fullViewModel = GraphViewModel(self.fullScene, model, self.fullViewState)
        self.fullView = QGraphicsView(self.fullScene)

        self.layout.addWidget(self.miniView)
        self.layout.addWidget(self.fullView)
