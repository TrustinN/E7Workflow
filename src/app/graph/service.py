import os

from nanoid import generate

from ..routing import Dispatcher, EndpointService, RequestType
from .model import GraphModel

GRAPH_SERVICE = "GRAPH SERVICE"


class GraphServiceRoute:
    GRAPH = "graph"
    NODE = "node"


class GraphService(EndpointService):
    def __init__(self, dispatcher: Dispatcher):
        super().__init__(GRAPH_SERVICE, dispatcher)

        self.addRoute(
            RequestType.POST,
            self._route(GraphServiceRoute.GRAPH),
            self.createGraph,
        )

        self.graphs: dict[str, GraphModel] = {}

    def createGraph(self, data):
        model = GraphModel()
        modelID = generate()
        self.graphs[modelID] = model
        self.addRoute(
            RequestType.POST,
            self._route(
                GraphServiceRoute.GRAPH,
                modelID,
                GraphServiceRoute.NODE,
            ),
            self.createNode,
        )
        return {"graphID": modelID}

    def createNode(self, data):
        nodeID = generate()
        graphID = data["graphID"]
        self.graphs[graphID].createNode(nodeID)

        return {"nodeID": nodeID}
