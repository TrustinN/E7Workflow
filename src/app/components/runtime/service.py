from src.router.routing import Dispatcher, EndpointService, RequestType, route

from .model import RuntimeModel, RuntimeSchema


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

        self.addRoute(RequestType.POST, route(RuntimeRoute.ITEM, ":id"), self.addItem)
        self.addRoute(RequestType.PUT, route(RuntimeRoute.ITEM, ":id"), self.updateItem)
        self.addRoute(RequestType.PUT, route(RuntimeRoute.ITEM), self.updateModel)

    def getItem(self, id, data):
        return self.model.getItem(id).toData()

    def getAllItems(self, data):
        return self.model.toData()

    def addItem(self, id, data):
        self.model.addItem(id, RuntimeSchema.fromData(data))

    def updateItem(self, id, data):
        self.model.updateItem(id, data)

    def updateModel(self, data):
        self.model.update(data)
