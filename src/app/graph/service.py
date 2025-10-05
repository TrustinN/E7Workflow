import json
from functools import partial

from src.router.routing import Dispatcher, EndpointService, RequestType, route

from .backend import GraphBackend


class GraphServiceData:
    NAME = "graphService"
    GRAPH = "graph"
    NODE = "node"
    EDGE = "edge"
    EXPORT = "export"
    IMPORT = "import"


gs = GraphServiceData


class GraphService(EndpointService):
    def __init__(self, dispatcher: Dispatcher, backend: GraphBackend):
        super().__init__(gs.NAME, dispatcher)

        self.backend = backend

        self.addRoute(RequestType.GET, route(gs.GRAPH), self.readGraph)
        self.addRoute(RequestType.POST, route(gs.GRAPH), self.createGraph)

        self.addRoute(RequestType.POST, route(gs.GRAPH, gs.EXPORT), self.exportGraph)
        self.addRoute(RequestType.POST, route(gs.GRAPH, gs.IMPORT), self.importGraph)

    def createGraph(self, data):
        userData = data.get("userData")
        graphID, graphData = self.backend.createGraph(userData=userData)

        nodeRoute = route(gs.GRAPH, graphID, gs.NODE)
        edgeRoute = route(gs.GRAPH, graphID, gs.EDGE)

        self.addRoute(RequestType.POST, nodeRoute, partial(self.createNode, graphID))
        self.addRoute(RequestType.POST, edgeRoute, partial(self.createEdge, graphID))

        return {"graphID": graphID, "graphData": graphData}

    def createNode(self, graphID, data):
        userData = data.get("userData")
        nodeID, nodeData = self.backend.createNode(graphID, userData=userData)

        nodeRoute = route(gs.GRAPH, graphID, gs.NODE, nodeID)
        self.addRoute(
            RequestType.PUT, nodeRoute, partial(self.updateNode, graphID, nodeID)
        )

        return {"nodeID": nodeID}

    def updateNode(self, graphID, nodeID, data):
        self.backend.updateNode(graphID, nodeID, data)

    def createEdge(self, graphID, data):
        id1 = data["nodeID1"]
        id2 = data["nodeID2"]
        userData = data.get("userData")

        edgeID, edgeData = self.backend.createEdge(graphID, id1, id2, userData=userData)

        return {"edgeID": edgeID}

    # Batch Operations
    def readGraph(self, data):
        return self.backend.graphs

    def exportGraph(self, data):
        path = data.get("outputFilename") or "graphConfig"
        with open(path, "w") as f:
            json.dump(self.backend.graphs, f, indent=4)

    def importGraph(self, data):
        path = data.get("outputFilename") or "graphConfig"
        self.deleteAllGraphs(data)

        with open(path, "r") as f:
            data = json.load(f)
            self.backend.overwrite(data)

    def deleteAllGraphs(self, data):
        self.backend.clear
