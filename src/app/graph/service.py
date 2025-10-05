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

        self.addRoute(RequestType.GET, route(gs.CONTEXT), self.getContext)
        self.addRoute(RequestType.POST, route(gs.CONTEXT), self.setContext)

        nodeRoute = route(gs.GRAPH, ":id", gs.NODE)
        edgeRoute = route(gs.GRAPH, ":id", gs.EDGE)

        self.addRoute(RequestType.POST, nodeRoute, self.createNode)
        self.addRoute(RequestType.POST, edgeRoute, self.createEdge)

        edgeRoute = route(gs.GRAPH, ":id", gs.EDGE, ":id")
        nodeRoute = route(gs.GRAPH, ":id", gs.NODE, ":id")
        self.addRoute(RequestType.PUT, edgeRoute, self.updateEdge)
        self.addRoute(RequestType.PUT, nodeRoute, self.updateNode)

        self.addRoute(RequestType.POST, route(gs.GRAPH, gs.EXPORT), self.exportGraph)
        self.addRoute(RequestType.POST, route(gs.GRAPH, gs.IMPORT), self.importGraph)

    def getContext(self, data):
        return self.backend.context

    def setContext(self, data):
        self.backend.setContext(data)

    def createGraph(self, data):
        userData = data.get("userData")
        graphID, graphData = self.backend.createGraph(userData=userData)

        return {"graphID": graphID, "graphData": graphData}

    def createNode(self, graphID, data):
        userData = data.get("userData")
        nodeID, nodeData = self.backend.createNode(graphID, userData=userData)

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

        path = data.get("contextFilename") or "graphContext"
        with open(path, "w") as f:
            json.dump(self.backend.context, f, indent=4)

    def importGraph(self, data):
        path = data.get("outputFilename") or "graphConfig"
        with open(path, "r") as f:
            data = json.load(f)
            self.backend.overwrite(data)

        path = data.get("contextFilename") or "graphContext"
        with open(path, "r") as f:
            data = json.load(f)
            self.backend.setContext(data)

    def deleteAllGraphs(self, data):
        self.backend.clear
