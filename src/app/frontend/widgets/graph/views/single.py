from src.app.frontend.widgets.graph.components import NodeType

from .multi import GraphMultiView


class GraphSingleView(GraphMultiView):
    def __init__(self):
        super().__init__()
        self.graphID = None

    def selectNode(self, nodeID: str):
        super().selectNode(nodeID, self.graphID)

    def unselectNode(self, nodeID: str):
        super().unselectNode(nodeID, self.graphID)

    def clearSelection(self):
        super().clearSelection(self.graphID)

    def createGraph(self, graphID: str):
        super().createGraph(graphID)
        self.graphID = graphID

    def createNode(self, nodeID: str, nodeType=NodeType.RECTANGLE):
        super().createNode(nodeID, self.graphID, nodeType)

    def createEdge(self, e1: str, e2: str):
        super().createEdge(e1, e2, self.graphID)

    def updateNode(self, nodeID: str, data):
        super().updateNode(nodeID, self.graphID, data)

    def updateEdge(self, e1: str, e2: str, data):
        super().updateEdge(e1, e2, self.graphID, data)

    def readNode(self, nodeID: str):
        return super().readNode(nodeID, self.graphID)

    def readEdge(self, e1: str, e2: str):
        return super().readEdge(e1, e2, self.graphID)

    def clearState(self):
        super().clearState()
        self.graphID = None
