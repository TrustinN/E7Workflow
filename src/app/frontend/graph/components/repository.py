from src.app.backend.graph.service import gs
from src.router.routing import Client, Dispatcher, Link


class GraphRepository:
    def __init__(self, dispatcher: Dispatcher):
        self.client = Client("Graph Repository", dispatcher)

    def createGraph(self):
        link = Link(gs.NAME, gs.GRAPH)
        response = self.client.post(link)
        sceneID = response["graphID"]

        return sceneID

    def updateGraph(self, graphID, data):
        link = Link(gs.NAME, gs.GRAPH, graphID)
        self.client.put(link, data)

    def createNode(self, graphID):
        link = Link(gs.NAME, gs.GRAPH, graphID, gs.NODE)
        response = self.client.post(link)

        nodeID = response["nodeID"]
        return nodeID

    def updateNode(self, graphID, nodeID, data):
        link = Link(gs.NAME, gs.GRAPH, graphID, gs.NODE, nodeID)
        self.client.put(link, data)

    def createEdge(self, graphID):
        link = Link(gs.NAME, gs.GRAPH, graphID, gs.EDGE)
        response = self.client.post(link)

        edgeID = response["edgeID"]
        return edgeID

    def updateEdge(self, graphID, edgeID, data):
        link = Link(gs.NAME, gs.GRAPH, graphID, gs.EDGE, edgeID)
        self.client.put(link, data)

    def getGraph(self):
        link = Link(gs.NAME, gs.GRAPH)
        return self.client.get(link)

    def exportGraph(self):
        link = Link(gs.NAME, gs.GRAPH, gs.EXPORT)
        self.client.post(link)

    def importGraph(self):
        link = Link(gs.NAME, gs.GRAPH, gs.IMPORT)
        self.client.post(link)
