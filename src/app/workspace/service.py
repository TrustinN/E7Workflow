import json

from src.router.routing import Dispatcher, EndpointService, RequestType, route

from .backend import WorkspaceBackend


class WorkspaceServiceData:
    NAME = "workspaceService"
    WORKSPACE = "workspace"
    EXPORT = "export"
    DELETE = "delete"


ws = WorkspaceServiceData


class WorkspaceService(EndpointService):
    def __init__(self, dispatcher: Dispatcher, backend: WorkspaceBackend):
        super().__init__(ws.NAME, dispatcher)

        self.backend = backend

        createRoute = route(ws.WORKSPACE)
        self.addRoute(RequestType.POST, createRoute, self.createWorkspace)

        batchReadRoute = route(ws.WORKSPACE)
        batchExportRoute = route(ws.WORKSPACE, ws.EXPORT)
        batchDeleteRoute = route(ws.WORKSPACE, ws.DELETE)
        self.addRoute(RequestType.GET, batchReadRoute, self.readAllWorkspaces)
        self.addRoute(RequestType.POST, batchExportRoute, self.exportWorkspace)
        self.addRoute(RequestType.POST, batchDeleteRoute, self.deleteAllWorkspaces)

    def createWorkspace(self, data):
        workspaceID, workspaceData = self.backend.createWorkspace(data)
        self.addRoute(
            RequestType.PUT,
            route(ws.WORKSPACE, workspaceID),
            self.updateWorkspaceFunc(workspaceID),
        )

        return {"workspaceID": workspaceID, "workspaceData": workspaceData}

    def updateWorkspaceFunc(self, id):
        def updateWorkspace(data):
            self.backend.updateWorkspace(id, data)

        return updateWorkspace

    # Batch Operations
    def readAllWorkspaces(self, data):
        return self.backend.workspaces

    def exportWorkspace(self, data):
        path = data.get("outputFilename") or "workspaceConfig"

        with open(path, "w") as f:
            json.dump(self.backend.workspaces, f, indent=4)

    def deleteAllWorkspaces(self, data):
        self.backend.clear()
