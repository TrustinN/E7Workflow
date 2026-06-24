from src.router.routing import Dispatcher, EndpointService, RequestType, route

from .actions import ActionType, ClickAction, DragAction
from .model import ActionModel


class ActionRoute:
    NAME = "ActionService"
    ACTION = "Action"
    CREATE = "Create"


ACTIONS = {
    ActionType.CLICK: ClickAction,
    ActionType.DRAG: DragAction,
}


class ActionService(EndpointService):

    def __init__(self, model: ActionModel, dispatcher: Dispatcher):
        super().__init__(ActionRoute.NAME, dispatcher)

        self.model = model

        # Create action
        createRoute = route(ActionRoute.CREATE)
        self.addRoute(RequestType.POST, createRoute, self.createAction)

        # Run action
        postRoute = route(ActionRoute.ACTION, ":id")
        self.addRoute(RequestType.POST, postRoute, self.runAction)

    def createAction(self):
        id = self.model.createAction()
        return {"id": id}

    def runAction(self, id, data):
        schema = self.model.getAction(id)
        actionCls = ACTIONS.get(schema.name)
        return actionCls().execute(schema.toData())
