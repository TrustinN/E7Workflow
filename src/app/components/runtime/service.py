from src.router.routing import Dispatcher, EndpointService, RequestType, route

from .model import RuntimeModel


class RuntimeRoute:
    NAME = "RuntimeService"
    ITEM = "ITEM"


class RuntimeService(EndpointService):
    def __init__(
        self,
        model: RuntimeModel,
        dispatcher: Dispatcher,
    ):
        super().__init__(RuntimeRoute.NAME, dispatcher)

        self.model = model

        self.addRoute(RequestType.GET, route(RuntimeRoute.ITEM, ":id"), self.getItem)
        self.addRoute(RequestType.GET, route(RuntimeRoute.ITEM), self.getAllItems)

    def getItem(self, id, data):
        return self.model.getItem(id).toData()

    def getAllItems(self, data):
        return self.model.toData()
