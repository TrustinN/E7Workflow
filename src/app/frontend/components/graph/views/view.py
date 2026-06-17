from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QGraphicsView, QVBoxLayout, QWidget

from src.app.frontend.widgets.graph.components import EdgeSchema, GraphScene, NodeSchema


class GraphView(QWidget):
    nodeCreated_ = pyqtSignal(str)
    edgeCreated_ = pyqtSignal(str)

    nodeUpdated_ = pyqtSignal(str)
    edgeUpdated_ = pyqtSignal(str)

    nodeSelected_ = pyqtSignal(str)
    nodeDeselected_ = pyqtSignal()

    edgeSelected_ = pyqtSignal(str)
    edgeDeselected_ = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.view = QGraphicsView()
        self.view.setFixedSize(400, 300)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.layout.addWidget(self.view)

    @property
    def scene(self) -> GraphScene:
        return self.view.scene()

    def setScene(self, scene):
        self.view.setScene(scene)

    def updateNode(self, nodeID: str, data: NodeSchema):
        pass

    def readNode(self, nodeID: str) -> NodeSchema:
        pass

    def readEdge(self, edgeID: str) -> EdgeSchema:
        pass

    def clearState(self):
        pass
