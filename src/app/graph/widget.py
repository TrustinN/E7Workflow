from nanoid import generate
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QGraphicsView, QPushButton, QVBoxLayout, QWidget

from .controller import GraphController


class GraphWidget(QWidget):

    def __init__(self, controller: GraphController):
        super().__init__()

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.view = QGraphicsView()
        self.view.setFixedSize(400, 300)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.controller = controller

        self.createNodeBtn = QPushButton("Create Node")
        self.createEdgeBtn = QPushButton("Create Edge")

        self.createNodeBtn.clicked.connect(self.createNode)
        self.createEdgeBtn.clicked.connect(self.createEdge)
        self.nodeStart = None

        self.layout.addWidget(self.view)
        self.layout.addWidget(self.createNodeBtn)
        self.layout.addWidget(self.createEdgeBtn)

    def setScene(self, scene):
        self.view.setScene(scene)

    def createNode(self):
        id = generate()
        self.controller.createNode(id)

    def createEdge(self):
        id1 = self.nodeStart
        id2 = self.controller.selectedNode()
        if not id2:
            return

        if not id1:
            self.nodeStart = id2
            return

        self.controller.createEdge(id1, id2)
        self.nodeStart = None
