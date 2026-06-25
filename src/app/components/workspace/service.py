from src.router.routing import Dispatcher, EndpointService, RequestType, route

from .model import WorkspaceModel


class WorkspaceRoute:
    NAME = "workspaceService"
    WORKSPACE = "workspace"
    EXPORT = "export"
    IMPORT = "import"


wr = WorkspaceRoute


class WorkspaceService(EndpointService):
    def __init__(self, model: WorkspaceModel, dispatcher: Dispatcher):
        super().__init__(wr.NAME, dispatcher)

        self.model = model

        self.addRoute(RequestType.GET, route(wr.WORKSPACE), self.listWorkspaces)
        self.addRoute(RequestType.GET, route(wr.WORKSPACE, ":id"), self.getWorkspace)
        self.addRoute(RequestType.PUT, route(wr.WORKSPACE, ":id"), self.updateWorkspace)

    def getWorkspace(self, id, data):
        return self.model.nodes[id].toData()

    def updateWorkspace(self, id, data):
        self.model.updateItem(id, data)

    def listWorkspaces(self, data):
        return {"workspaces": list(self.model.nodes.keys())}
