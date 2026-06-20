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

    def selectEdge(self, edgeID: str):
        super().selectEdge(edgeID, self.graphID)

    def unselectEdge(self, edgeID: str):
        super().unselectEdge(edgeID, self.graphID)

    def clearSelection(self):
        super().clearSelection(self.graphID)

    def createGraph(self, graphID: str):
        super().createGraph(graphID)
        self.graphID = graphID

    def createNode(self, nodeID: str, nodeType=NodeType.RECTANGLE):
        super().createNode(nodeID, self.graphID, nodeType)

    def createEdge(self, edgeID: str, e1: str, e2: str):
        super().createEdge(edgeID, e1, e2, self.graphID)

    def clearState(self):
        super().clearState()
        self.graphID = None
