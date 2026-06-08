from PyQt5.QtWidgets import QVBoxLayout, QWidget

from src.app.frontend.models import GraphModel, TreeModel
from src.app.frontend.state import SelectionModel

from .node import GraphNode
from .views import GraphFullView, GraphMiniView
from .widgets import GraphButtons


class GraphComponent(QWidget):

    def __init__(self, selectionModel: SelectionModel):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.buttons = GraphButtons()

        self.graphModel = GraphModel()
        self.graphFullViewModel = GraphModel()
        self.graphMiniViewModel = TreeModel()

        self.node = GraphNode(
            self.graphModel,
            self.graphFullViewModel,
            self.graphMiniViewModel,
            selectionModel,
            self.buttons,
        )

        self.miniView = GraphMiniView(
            self.graphModel,
            self.graphMiniViewModel,
            selectionModel,
        )
        self.fullView = GraphFullView(
            self.graphModel,
            self.graphFullViewModel,
            selectionModel,
        )

        self.layout.addWidget(self.miniView)
        self.layout.addWidget(self.fullView)
