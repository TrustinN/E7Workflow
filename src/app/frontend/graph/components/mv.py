from PyQt5.QtCore import QObject, pyqtSignal

from .controller import GraphController
from .view import GraphView


class GraphMV(QObject):
    nodeSelected_ = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.controllers = {}
        self.views = {}

        # One to one mapping of graph/node -> data
        self.graphDataID = {}
        self.dataGraphID = {}

        self.nodeDataID = {}
        self.dataNodeID = {}

        self.nodeParents = {}

    def setNodeData(self, node, data):
        self.nodeDataID[node] = data
        self.dataNodeID[data] = node

    def setGraphData(self, graph, data):
        self.graphDataID[graph] = data
        self.dataGraphID[data] = graph

    def nodeData(self, node):
        return self.nodeDataID[node]

    def graphData(self, graph):
        return self.graphDataID[graph]

    def dataNode(self, data):
        return self.dataNodeID[data]

    def dataGraph(self, data):
        return self.dataGraphID[data]

    def controller(self, graphID):
        return self.controllers[graphID]

    def controllerIDs(self):
        return list(self.controllers.keys())

    def view(self, graphID):
        return self.views[graphID]

    def createController(self, graphID):
        view = GraphView()
        controller = GraphController(view)

        view.nodePressed_.connect(self.nodeSelected_.emit)

        self.controllers[graphID] = controller
        self.views[graphID] = view
        return graphID

    def createGraph(self, graphID):
        self.createController(graphID)
        return graphID

    def createNode(self, graphID, nodeID):
        controller = self.controller(graphID)
        controller.createNode(nodeID)
        self.nodeParents[nodeID] = graphID

        return nodeID

    def updateNode(self, nodeID, data):
        graphID = self.nodeParents[nodeID]
        controller = self.controller(graphID)
        controller.updateNode(nodeID, data)

    def createEdge(self, graphID, edgeID, node1, node2):
        controller = self.controller(graphID)
        controller.createEdge(edgeID, node1, node2)

    def clear(self):
        for view in self.views.values():
            view.deleteLater()

        self.views.clear()
        self.controllers.clear()

        self.graphDataID.clear()
        self.dataGraphID.clear()

        self.nodeDataID.clear()
        self.dataNodeID.clear()

        self.nodeParents.clear()
