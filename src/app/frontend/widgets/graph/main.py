from PyQt5.QtWidgets import QVBoxLayout, QWidget

from src.app.frontend.state import Context

from .components import GraphButtons
from .controllers import GraphFullViewController, GraphMiniViewController
from .node import GraphNode
from .views import GraphMultiView, GraphSingleView


class GraphComponent(QWidget):

    def __init__(self, context: Context):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.context = context

        self.miniView = GraphMultiView()
        self.fullView = GraphSingleView()

        self.miniViewController = GraphMiniViewController(
            self.context,
            self.miniView,
        )
        self.fullViewController = GraphFullViewController(
            self.context,
            self.fullView,
        )

        self.node = GraphNode(self.context)

        self.buttons = GraphButtons()
        self.buttons.setE1Btn.clicked.connect(self.node.setE1)
        self.buttons.setE2Btn.clicked.connect(self.node.setE2)

        self.layout.addWidget(self.miniView)
        self.layout.addWidget(self.fullView)
        self.layout.addWidget(self.buttons)
