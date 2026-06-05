from nanoid import generate

from src.app.frontend.events import Node
from src.app.frontend.graph.components import GraphMV, GraphSerializer
from src.app.frontend.graph.widgets import GraphButtonsWidget, GraphViewWidget


class GraphMiniView(Node):
    def __init__(self, view: GraphViewWidget, buttons: GraphButtonsWidget):
        super().__init__()
        self.buttons = buttons
        self.view = view

        self.graphmv = GraphMV()
        self.serializer = GraphSerializer(self.graphmv)
        self.activeSceneID = None

        self.buttons.setE1Btn.clicked.connect(self.setE1)
        self.buttons.setE2Btn.clicked.connect(self.setE2)
        self.buttons.createEdgeBtn.clicked.connect(self.createEdge)
        self.e1 = None
        self.e2 = None

        self.subscribe("/WS Component/RootWSCreated", self.createRootNode)
        self.subscribe("/WS Component/WSCreated", self.createNode)
        self.subscribe("/WS Component/WSFocused", self.setGraph)
        self.subscribe("/WS Component/WSExport", self.graphExport)
        self.subscribe("/WS Component/WSImport", self.graphImport)

    def createRootNode(self, data):
        graphID = generate()
        graphID = self.graphmv.createGraph(graphID)
        parent = self.view.scene

        if parent is None:
            view = self.graphmv.view(graphID)
            self.view.setScene(view)
            self.activeSceneID = graphID

        wkID = data["id"]
        self.graphmv.setGraphData(graphID, wkID)

    def createNode(self, data):
        graphID = generate()
        self.graphmv.createGraph(graphID)

        nodeID = generate()
        self.graphmv.createNode(self.activeSceneID, nodeID)

        wkID = data["id"]
        wkName = data["text"]
        self.graphmv.setNodeData(nodeID, wkID)
        self.graphmv.setGraphData(graphID, wkID)
        self.graphmv.updateNode(nodeID, {"displayText": wkName})

    def setGraph(self, data):
        wkID = data["id"]
        graphID = self.graphmv.dataGraph(wkID)
        view = self.graphmv.view(graphID)
        self.view.setScene(view)
        self.activeSceneID = graphID

    def setE1(self):
        view = self.graphmv.view(self.activeSceneID)
        self.e1 = view.selectedNode()

    def setE2(self):
        view = self.graphmv.view(self.activeSceneID)
        self.e2 = view.selectedNode()

    def createEdge(self):
        if not (self.e1 and self.e2):
            return

        edgeID = generate()
        self.graphmv.createEdge(self.activeSceneID, edgeID, self.e1, self.e2)
        self.e1 = None
        self.e2 = None

    def graphExport(self, data):
        self.serializer.export()

    def graphImport(self, data):
        self.serializer.restore()
