from src.router.routing import Dispatcher, EndpointService, RequestType, route

from .backend import RunnerBackend


class RunnerServiceData:
    NAME = "runnerService"
    STATE = "state"
    ACTION = "action"
    TRANSITION = "transition"
    EXPORT = "export"
    IMPORT = "import"


rs = RunnerServiceData


class RunnerService(EndpointService):
    def __init__(self, dispatcher: Dispatcher, backend: RunnerBackend):
        super().__init__(rs.NAME, dispatcher)

        self.backend = backend

        createStateR = route(rs.STATE)
        updateStateR = route(rs.STATE, ":id")
        self.addRoute(RequestType.POST, createStateR, self.createState)
        self.addRoute(RequestType.PUT, updateStateR, self.updateState)

        createActionR = route(rs.ACTION)
        updateActionR = route(rs.ACTION, ":id")
        self.addRoute(RequestType.POST, createActionR, self.createAction)
        self.addRoute(RequestType.PUT, updateActionR, self.updateAction)

        createTransitionR = route(rs.TRANSITION, ":id", ":id")
        self.addRoute(RequestType.POST, createTransitionR, self.createTransition)

    def createState(self, data):
        stateID, stateData = self.backend.createState(data)

        return {"stateID": stateID, "stateData": stateData}

    def updateState(self, id, data):
        self.backend.updateState(id, data)

    def createAction(self, data):
        actionID = self.backend.createAction(data)

        return {"actionID": actionID}

    def updateAction(self, id, data):
        self.backend.updateAction(id, data)

    def createTransition(self, id1, id2, data):
        self.backend.createTransition(id1, id2, data)
