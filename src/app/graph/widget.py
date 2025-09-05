from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGraphicsView, QPushButton, QVBoxLayout, QWidget

from ..routing import Dispatcher, Endpoint, RequestType, route
from .controller import GraphController
from .graph import InteractiveGraphScene
from .service import GRAPH_SERVICE, GraphServiceRoute
from .view import GraphView


class GraphWidget(QWidget):

    def __init__(self, dispatcher: Dispatcher):
        super().__init__()

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.view = QGraphicsView()
        self.view.setFixedSize(400, 300)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.endpoint = Endpoint("Graph Widget", dispatcher)
        self.controllers: dict[str, GraphController] = {}
        self.activeGraph: str = None

        self.createGraphBtn = QPushButton("Create Graph")
        self.createNodeBtn = QPushButton("Create Node")
        self.createEdgeBtn = QPushButton("Create Edge")

        self.createGraphBtn.clicked.connect(self.createGraph)
        self.createNodeBtn.clicked.connect(self.createNode)
        self.createEdgeBtn.clicked.connect(self.createEdge)
        self.nodeStart = None

        self.layout.addWidget(self.view)
        self.layout.addWidget(self.createGraphBtn)
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
        response = self.endpoint.send(
            {},
            RequestType.POST,
            route(GraphServiceRoute.GRAPH),
            GRAPH_SERVICE,
        )
        graphID = response["graphID"]
        graphModel = response["graphModel"]
        scene = InteractiveGraphScene()
        graphView = GraphView(scene)
        controller = GraphController(graphModel, graphView)
        self.controllers[graphID] = controller

        self.setActiveGraph(graphID)

    def createNode(self):
        self.endpoint.send(
            {},
            RequestType.POST,
            route(
                GraphServiceRoute.GRAPH,
                self.activeGraph,
                GraphServiceRoute.NODE,
            ),
            GRAPH_SERVICE,
        )

    def createEdge(self):
        id1 = self.nodeStart
        id2 = self.controller.selectedNode()
        if not id2:
            return

        if not id1:
            self.nodeStart = id2
            return

        self.endpoint.send(
            {"nodeID1": id1, "nodeID2": id2},
            RequestType.POST,
            route(
                GraphServiceRoute.GRAPH,
                self.activeGraph,
                GraphServiceRoute.EDGE,
            ),
            GRAPH_SERVICE,
        )
        self.nodeStart = None
