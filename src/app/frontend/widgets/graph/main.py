from PyQt5.QtWidgets import QVBoxLayout, QWidget

from src.app.frontend.state import GraphModel, TreeModel, WorkspaceContext

from .components import GraphButtons
from .node import GraphNode
from .views import GraphFullView, GraphMiniView


class GraphComponent(QWidget):

    def __init__(self, context: WorkspaceContext):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.context = context
        self.graphFullViewModel = GraphModel()
        self.graphMiniViewModel = TreeModel()

        self.node = GraphNode(
            self.context,
            self.graphFullViewModel,
            self.graphMiniViewModel,
        )

        self.miniView = GraphMiniView(
            self.context,
            self.graphMiniViewModel,
        )
        self.fullView = GraphFullView(
            self.context,
            self.graphFullViewModel,
        )

        self.buttons = GraphButtons()
        self.buttons.setE1Btn.clicked.connect(self.node.setE1)
        self.buttons.setE2Btn.clicked.connect(self.node.setE2)
        self.buttons.createEdgeBtn.clicked.connect(self.node.createEdge)

        self.layout.addWidget(self.miniView)
        self.layout.addWidget(self.fullView)
