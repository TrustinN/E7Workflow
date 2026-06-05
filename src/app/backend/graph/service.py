import json

from src.router.routing import Dispatcher, EndpointService, RequestType, route

from .backend import GraphBackend


class GraphServiceData:
    NAME = "graphService"
    GRAPH = "graph"
    NODE = "node"
    EDGE = "edge"
    EXPORT = "export"
    IMPORT = "import"
    CONTEXT = "context"


gs = GraphServiceData


class GraphService(EndpointService):
    def __init__(self, dispatcher: Dispatcher, backend: GraphBackend):
        super().__init__(gs.NAME, dispatcher)

        self.backend = backend

        self.addRoute(RequestType.GET, route(gs.GRAPH), self.readGraph)
        self.addRoute(RequestType.POST, route(gs.GRAPH), self.createGraph)

        nodeRoute = route(gs.GRAPH, ":id", gs.NODE)
        edgeRoute = route(gs.GRAPH, ":id", gs.EDGE)

        self.addRoute(RequestType.POST, nodeRoute, self.createNode)
        self.addRoute(RequestType.POST, edgeRoute, self.createEdge)

        graphRoute = route(gs.GRAPH, ":id")
        edgeRoute = route(gs.GRAPH, ":id", gs.EDGE, ":id")
        nodeRoute = route(gs.GRAPH, ":id", gs.NODE, ":id")

        self.addRoute(RequestType.PUT, graphRoute, self.updateGraph)
        self.addRoute(RequestType.PUT, edgeRoute, self.updateEdge)
        self.addRoute(RequestType.PUT, nodeRoute, self.updateNode)

        self.addRoute(RequestType.POST, route(gs.GRAPH, gs.EXPORT), self.exportGraph)
        self.addRoute(RequestType.POST, route(gs.GRAPH, gs.IMPORT), self.importGraph)

    def createGraph(self, data):
        graphID, graphData = self.backend.createGraph(data)

        return {"graphID": graphID, "graphData": graphData}

    def updateGraph(self, graphID, data):
        self.backend.updateGraph(graphID, data)

    def createNode(self, graphID, data):
        nodeID, nodeData = self.backend.createNode(graphID, data)

        return {"nodeID": nodeID}

    def updateNode(self, graphID, nodeID, data):
        self.backend.updateNode(graphID, nodeID, data)

    def createEdge(self, graphID, data):
        edgeID, edgeData = self.backend.createEdge(graphID, data)

        return {"edgeID": edgeID}

    def updateEdge(self, graphID, edgeID, data):
        self.backend.updateEdge(graphID, edgeID, data)

    # Batch Operations
    def readGraph(self, data):
        return self.backend.graphs

    def exportGraph(self, data):
        path = data.get("outputFilename") or "graphConfig"
        with open(path, "w") as f:
            json.dump(self.backend.graphs, f, indent=4)

    def importGraph(self, data):
        path = data.get("outputFilename") or "graphConfig"
        with open(path, "r") as f:
            data = json.load(f)
            self.backend.overwrite(data)

    def deleteAllGraphs(self, data):
        self.backend.clear()
