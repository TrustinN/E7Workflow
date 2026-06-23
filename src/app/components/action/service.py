from src.router.routing import Dispatcher, EndpointService, RequestType, route

from .actions import ClickAction, DragAction


class ActionRoute:
    NAME = "ActionService"
    ACTION = "Action"


class ActionType:
    CLICK = "Click"
    DRAG = "Drag"


class ActionService(EndpointService):
    actionTypes = {
        ActionType.CLICK: ClickAction,
        ActionType.DRAG: DragAction,
    }

    def __init__(self, dispatcher: Dispatcher):
        super().__init__(ActionRoute.NAME, dispatcher)

        # Get data about action like user params
        getRoute = route(ActionRoute.ACTION, ":id")
        self.addRoute(RequestType.GET, getRoute, self.getAction)

        # Run action
        postRoute = route(ActionRoute.ACTION, ":id")
        self.addRoute(RequestType.POST, postRoute, self.postAction)

    def getAction(self, id, data):
        actionCls = self.actionTypes[id]
        return actionCls.info()

    def postAction(self, id, data):
        actionCls = self.actionTypes[id]
        action = actionCls()
        return action.execute(data)
