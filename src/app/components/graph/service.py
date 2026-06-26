from src.router.routing import Dispatcher, EndpointService, RequestType, route

from .model import GraphModel


class GraphRoute:
    NAME = "GraphService"
    NODE = "NODE"
    EDGE = "EDGE"


class GraphService(EndpointService):
    def __init__(self, model: GraphModel, dispatcher: Dispatcher):
        super().__init__(GraphRoute.NAME, dispatcher)

        self.model = model

        self.addRoute(RequestType.GET, route(GraphRoute.NODE, ":id"), self.getNode)
        self.addRoute(RequestType.GET, route(GraphRoute.EDGE, ":id"), self.getEdge)

        self.addRoute(
            RequestType.GET,
            route(GraphRoute.NODE, ":id", GraphRoute.EDGE),
            self.getNodeEdges,
        )

    def getNode(self, id, data):
        node = self.model.getNode(id)
        return node.toData()

    def getEdge(self, id, data):
        edge = self.model.getEdge(id)
        return edge.toData()

    def getNodeEdges(self, id, data):
        edges = self.model.getNodeEdges(id)
        return {"edges": edges}
