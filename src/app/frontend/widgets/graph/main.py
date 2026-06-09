from PyQt5.QtWidgets import QVBoxLayout, QWidget

from src.app.frontend.state import GraphModel, TreeModel, WorkspaceContext

from .components import GraphButtons
from .controllers import GraphFullViewController, GraphMiniViewController
from .node import GraphNode
from .views import GraphMultiView


class GraphComponent(QWidget):

    def __init__(self, context: WorkspaceContext):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.context = context
        self.graphFullViewModel = GraphModel()
        self.graphMiniViewModel = TreeModel()

        self.miniView = GraphMultiView()
        self.fullView = GraphMultiView()

        self.miniViewController = GraphMiniViewController(
            self.context,
            self.miniView,
            self.graphMiniViewModel,
        )
        self.fullViewController = GraphFullViewController(
            self.context,
            self.fullView,
            self.graphFullViewModel,
        )

        self.node = GraphNode(
            self.context,
            self.graphFullViewModel,
            self.graphMiniViewModel,
            self.fullViewController,
            self.miniViewController,
        )

        self.buttons = GraphButtons()
        self.buttons.setE1Btn.clicked.connect(self.node.setE1)
        self.buttons.setE2Btn.clicked.connect(self.node.setE2)

        self.layout.addWidget(self.miniView)
        self.layout.addWidget(self.fullView)
        self.layout.addWidget(self.buttons)
