from src.router.routing import Dispatcher, EndpointService, RequestType, route

from .actions import ActionType, ClickAction, DragAction
from .model import ActionModel, ActionViewModel


class ActionRoute:
    NAME = "ActionService"
    ACTION = "Action"
    CREATE = "Create"


ACTIONS = {
    ActionType.CLICK: ClickAction,
    ActionType.DRAG: DragAction,
}


class ActionService(EndpointService):

    def __init__(
        self,
        model: ActionModel,
        viewModel: ActionViewModel,
        dispatcher: Dispatcher,
    ):
        super().__init__(ActionRoute.NAME, dispatcher)

        self.model = model
        self.viewModel = viewModel

        # Create action
        createRoute = route(ActionRoute.CREATE)
        self.addRoute(RequestType.POST, createRoute, self.createAction)

        actionRoute = route(ActionRoute.ACTION, ":id")

        self.addRoute(RequestType.GET, actionRoute, self.getAction)
        self.addRoute(RequestType.POST, actionRoute, self.runAction)
        self.addRoute(RequestType.DELETE, actionRoute, self.deleteAction)

    def createAction(self, data):
        schema = self.viewModel.getDraft()
        id = self.model.createAction(schema)
        return {"id": id, "schema": schema.toData()}

    def getAction(self, id, data):
        schema = self.model.getAction(id)
        return schema.toData()

    def deleteAction(self, id, data):
        self.model.deleteAction(id)

    def runAction(self, id, data):
        schema = self.model.getAction(id)
        schema.update(data)
        actionCls = ACTIONS.get(schema.name)
        return actionCls().execute(schema.toData())
