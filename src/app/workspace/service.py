from nanoid import generate

from src.router.routing import Dispatcher, EndpointService, RequestType, route

from .model import WorkspaceModel, WorkspaceTreeModel

WORKSPACE_SERVICE = "WORKSPACE SERVICE"


class WorkspaceServiceRoute:
    WORKSPACE = "workspace"


class WorkspaceService(EndpointService):
    def __init__(self, dispatcher: Dispatcher):
        super().__init__(WORKSPACE_SERVICE, dispatcher)

        self.treeModel: WorkspaceTreeModel = WorkspaceTreeModel()
        self.workspaces: dict[str, WorkspaceModel] = self.treeModel.models

        self.addRoute(
            RequestType.GET,
            route(WorkspaceServiceRoute.WORKSPACE),
            self.getTreeModel,
        )

        self.addRoute(
            RequestType.POST,
            route(WorkspaceServiceRoute.WORKSPACE),
            self.createWorkspace,
        )

    def getTreeModel(self, data):
        return {"treeModel": self.treeModel}

    def createWorkspace(self, data):
        model = WorkspaceModel()
        modelID = generate()

        self.treeModel.createWorkspace(modelID)
        self.treeModel.updateWorkspace(modelID, model.data)

        return {"workspaceID": modelID, "workspaceModel": model}
