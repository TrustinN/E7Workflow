from nanoid import generate

from src.router.routing import Dispatcher, EndpointService, RequestType, route

# from .model import WorkspaceData, WorkspaceModel, WorkspaceTreeModel
from .backend import WorkspaceBackend


class WorkspaceServiceData:
    NAME = "workspaceService"
    WORKSPACE = "workspace"


ws = WorkspaceServiceData


class WorkspaceService(EndpointService):
    def __init__(self, dispatcher: Dispatcher, backend: WorkspaceBackend):
        super().__init__(ws.NAME, dispatcher)

        self.backend = backend

        self.addRoute(RequestType.POST, route(ws.WORKSPACE), self.createWorkspace)

    def createWorkspace(self, data):
        parent = data.get("parentID")
        workspaceID, workspaceData = self.backend.createWorkspace(parent)
        self.addRoute(
            RequestType.PUT,
            route(ws.WORKSPACE, workspaceID),
            self.updateWorkspaceFunc(workspaceID),
        )

        return {"workspaceID": workspaceID, "workspaceData": workspaceData}

    def updateWorkspaceFunc(self, id):
        def updateWorkspace(data):
            userData = data.get("userData")
            self.backend.updateWorkspace(id, userData)

        return updateWorkspace
