from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QGraphicsView, QPushButton, QVBoxLayout, QWidget

from src.router.routing import Client, Dispatcher, Link

from .controller import GraphController
from .graph import InteractiveGraphScene
from .service import GRAPH_SERVICE, GraphServiceRoute
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
        response = self.client.post(
            Link(GRAPH_SERVICE, GraphServiceRoute.GRAPH),
            {},
        )
        graphID = response["graphID"]
        graphModel = response["graphModel"]
        scene = InteractiveGraphScene()
        graphView = GraphView(scene)
        controller = GraphController(graphModel, graphView)
        self.controllers[graphID] = controller

        self.graphCreated_.emit(graphID)

    def createNode(self):
        response = self.client.post(
            Link(
                GRAPH_SERVICE,
                GraphServiceRoute.GRAPH,
                self.activeGraph,
                GraphServiceRoute.NODE,
            ),
            {},
        )
        nodeID = response["nodeID"]
        self.nodeCreated_.emit(nodeID)

    def createEdge(self):
        id1 = self.nodeStart
        id2 = self.controller.selectedNode()
        if not id2:
            return

        if not id1:
            self.nodeStart = id2
            return

        self.client.post(
            Link(
                GRAPH_SERVICE,
                GraphServiceRoute.GRAPH,
                self.activeGraph,
                GraphServiceRoute.EDGE,
            ),
            {"nodeID1": id1, "nodeID2": id2},
        )
        self.edgeCreated_.emit(id1, id2)
        self.nodeStart = None
