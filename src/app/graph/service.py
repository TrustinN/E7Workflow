from nanoid import generate

from ..routing import Dispatcher, EndpointService, RequestType, route
from .model import GraphModel

GRAPH_SERVICE = "GRAPH SERVICE"


class GraphServiceRoute:
    GRAPH = "graph"
    NODE = "node"
    EDGE = "edge"


class GraphService(EndpointService):
    def __init__(self, dispatcher: Dispatcher):
        super().__init__(GRAPH_SERVICE, dispatcher)

        self.addRoute(
            RequestType.POST,
            route(GraphServiceRoute.GRAPH),
            self.createGraph,
        )

        self.graphs: dict[str, GraphModel] = {}

    def createGraph(self, data):
        model = GraphModel()
        modelID = generate()
        self.graphs[modelID] = model

        self.addRoute(
            RequestType.POST,
            route(
                GraphServiceRoute.GRAPH,
                modelID,
                GraphServiceRoute.NODE,
            ),
            self.createNodeFunc(modelID),
        )

        self.addRoute(
            RequestType.POST,
            route(
                GraphServiceRoute.GRAPH,
                modelID,
                GraphServiceRoute.EDGE,
            ),
            self.createEdgeFunc(modelID),
        )
        return {"graphID": modelID, "graphModel": model}

    def createNodeFunc(self, graphID):
        def createNode(data):
            nodeID = generate()
            self.graphs[graphID].createNode(nodeID)

            return {"nodeID": nodeID}

        return createNode

    def createEdgeFunc(self, graphID):
        def createEdge(data):
            id1 = data["nodeID1"]
            id2 = data["nodeID2"]

            self.graphs[graphID].createEdge(id1, id2)

            return {}

        return createEdge
