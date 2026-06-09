from PyQt5.QtWidgets import QVBoxLayout, QWidget

from src.app.frontend.state import GraphModel, TreeModel, WorkspaceContext

from .node import GraphNode
from .views import GraphFullView, GraphMiniView
from .widgets import GraphButtons


class GraphComponent(QWidget):

    def __init__(self, context: WorkspaceContext):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.buttons = GraphButtons()

        self.context = context
        self.graphFullViewModel = GraphModel()
        self.graphMiniViewModel = TreeModel()

        self.node = GraphNode(
            self.context,
            self.graphFullViewModel,
            self.graphMiniViewModel,
            self.buttons,
        )

        self.miniView = GraphMiniView(
            self.context,
            self.graphMiniViewModel,
        )
        self.fullView = GraphFullView(
            self.context,
            self.graphFullViewModel,
        )

        self.layout.addWidget(self.miniView)
        self.layout.addWidget(self.fullView)
