from PyQt5.QtWidgets import QVBoxLayout, QWidget

from .mvc import GraphFullView, GraphMiniView, GraphModel
from .node import GraphNode
from .widgets import GraphButtonsWidget


class GraphComponent(QWidget):

    def __init__(self, selectionModel):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.graphModel = GraphModel()
        self.graphMiniViewModel = GraphModel()
        self.graphFullViewModel = GraphModel()

        self.node = GraphNode(self.graphModel)

        self.buttons = GraphButtonsWidget()
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
        self.layout.addWidget(self.buttons)
