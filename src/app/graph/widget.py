from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QGraphicsView, QPushButton, QVBoxLayout, QWidget

from src.router.routing import Client, Dispatcher, Link

from .controller import GraphController
from .graph import InteractiveGraphScene
from .service import gs
from .view import GraphView


class GraphWidget(QWidget):
    graphCreated_ = pyqtSignal(str)
    nodeCreated_ = pyqtSignal(str)
    edgeCreated_ = pyqtSignal(str, str)

    def __init__(self, dispatcher: Dispatcher):
        super().__init__()

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.view = QGraphicsView()
        self.view.setFixedSize(400, 300)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.client = Client("Graph Widget", dispatcher)
        self.controllers: dict[str, GraphController] = {}
        self.activeGraph: str = None

        self.createNodeBtn = QPushButton("Create Node")
        self.createEdgeBtn = QPushButton("Create Edge")

        self.createNodeBtn.clicked.connect(self.createNode)
        self.createEdgeBtn.clicked.connect(self.createEdge)
        self.nodeStart = None

        self.layout.addWidget(self.view)
        self.layout.addWidget(self.createNodeBtn)
        self.layout.addWidget(self.createEdgeBtn)

    @property
    def controller(self):
        return self.controllers[self.activeGraph]

    def setActiveGraph(self, id):
        self.activeGraph = id
        scene = self.controller.view.scene
        self.view.setScene(scene)

    def createGraph(self):
        link = Link(gs.NAME, gs.GRAPH)
        response = self.client.post(link)
        graphID = response["graphID"]
        graphData = response["graphData"]["data"]
        scene = InteractiveGraphScene()
        graphView = GraphView(scene)
        controller = GraphController(graphData, graphView)
        self.controllers[graphID] = controller

        self.graphCreated_.emit(graphID)

    def createNode(self):
        link = Link(gs.NAME, gs.GRAPH, self.activeGraph, gs.NODE)
        response = self.client.post(link)
        nodeID = response["nodeID"]
        self.controller.createNode(nodeID)
        self.nodeCreated_.emit(nodeID)

    def createEdge(self):
        id1 = self.nodeStart
        id2 = self.controller.selectedNode()
        if not id2:
            return

        if not id1:
            self.nodeStart = id2
            return

        link = Link(gs.NAME, gs.GRAPH, self.activeGraph, gs.EDGE)
        self.client.post(link, {"nodeID1": id1, "nodeID2": id2})
        self.controller.createEdge(id1, id2)
        self.edgeCreated_.emit(id1, id2)
        self.nodeStart = None
