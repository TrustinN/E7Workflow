from PyQt5.QtWidgets import QGraphicsView, QVBoxLayout, QWidget

from src.app.components.graph.model import GraphModel
from src.app.state import Context

from .controllers import GraphMiniViewController
from .scene import GraphScene


class GraphEditor(QWidget):
    def __init__(self, context: Context, model: GraphModel):
        super().__init__()

        self.layout = QVBoxLayout(self)

        self.scene = GraphScene(model)
        self.fullView = GraphMiniViewController(context, self.scene, model)
        self.view = QGraphicsView(self.scene)

        self.layout.addWidget(self.view)
