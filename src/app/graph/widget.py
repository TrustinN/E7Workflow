from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QGraphicsView, QVBoxLayout, QWidget

from .view import GraphView


class GraphWidget(QWidget):
    graphCreated_ = pyqtSignal(str)
    nodeCreated_ = pyqtSignal(str)
    edgeCreated_ = pyqtSignal(str, str)

    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.view = QGraphicsView()
        self.view.setFixedSize(400, 300)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.scenes: dict[str, GraphView] = {}
        self.activeGraph: str = None

        self.layout.addWidget(self.view)

    @property
    def scene(self):
        return self.scenes[self.activeGraph]

    def setActiveGraph(self, id):
        self.activeGraph = id
        scene = self.scene
        self.view.setScene(scene)

    def createGraph(self, id):
        self.scenes[id] = GraphView()
        self.graphCreated_.emit(id)

    def createNode(self, id):
        self.scene.createNode(id)
        self.nodeCreated_.emit(id)

    def createEdge(self, id1, id2):
        self.scene.createEdge(id1, id2)
        self.edgeCreated_.emit(id1, id2)
