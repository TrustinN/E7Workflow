from src.router.routing import Client, Dispatcher, Link

from .service import gs
from .view import GraphView


class GraphController:
    def __init__(self, dispatcher: Dispatcher):
        self.client = Client("Graph Controller", dispatcher)
        self.nodeStart = None

    def createGraph(self):
        link = Link(gs.NAME, gs.GRAPH)
        response = self.client.post(link)

        graphID = response["graphID"]
        return GraphView(), graphID

    def createNode(self, view, viewID):
        link = Link(gs.NAME, gs.GRAPH, viewID, gs.NODE)
        response = self.client.post(link)

        nodeID = response["nodeID"]
        view.createNode(nodeID)
        return nodeID

    def createEdge(self, view, viewID):
        id1 = self.nodeStart
        id2 = view.selectedNode()
        if not id2:
            return None

        if not id1:
            self.nodeStart = id2
            return None

        link = Link(gs.NAME, gs.GRAPH, viewID, gs.EDGE)
        self.client.post(link, {"nodeID1": id1, "nodeID2": id2})
        self.nodeStart = None
        view.createEdge(id1, id2)
        return (id1, id2)

    def updateNode(self, view, viewID, nodeID, data):
        view.updateNode(nodeID, data)
