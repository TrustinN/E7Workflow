from src.router.routing import Dispatcher, EndpointService, RequestType, route

from .backend import GraphBackend


class GraphServiceData:
    NAME = "graphService"
    GRAPH = "graph"
    NODE = "node"
    EDGE = "edge"


gs = GraphServiceData


class GraphService(EndpointService):
    def __init__(self, dispatcher: Dispatcher, backend: GraphBackend):
        super().__init__(gs.NAME, dispatcher)

        self.backend = backend
        self.addRoute(
            RequestType.POST,
            route(gs.GRAPH),
            self.createGraph,
        )

    def createGraph(self, data):
        userData = data.get("userData")
        graphID, graphData = self.backend.createGraph(userData=userData)

        self.addRoute(
            RequestType.POST,
            route(gs.GRAPH, graphID, gs.NODE),
            self.createNodeHandler(graphID),
        )

        self.addRoute(
            RequestType.POST,
            route(gs.GRAPH, graphID, gs.EDGE),
            self.createEdgeHandler(graphID),
        )
        return {"graphID": graphID, "graphData": graphData}

    def createNodeHandler(self, graphID):
        def createNode(data):
            userData = data.get("userData")
            nodeID, nodeData = self.backend.createNode(graphID, userData=userData)

            return {"nodeID": nodeID}

        return createNode

    def createEdgeHandler(self, graphID):
        def createEdge(data):
            id1 = data["nodeID1"]
            id2 = data["nodeID2"]
            userData = data.get("userData")

            edgeID, edgeData = self.backend.createEdge(
                graphID, id1, id2, userData=userData
            )

            return {"edgeID": edgeID}

        return createEdge
