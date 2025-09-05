from nanoid import generate

from src.router.routing import Dispatcher, EndpointService, RequestType, route

from .model import WorkspaceData, WorkspaceModel, WorkspaceTreeModel

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

        self.addRoute(
            RequestType.PUT,
            route(WorkspaceServiceRoute.WORKSPACE, modelID),
            self.updateWorkspaceFunc(modelID),
        )

        return {"workspaceID": modelID, "workspaceModel": model}

    def updateWorkspaceFunc(self, id):
        def updateWorkspace(data):
            text = data.get("text")
            parentID = data.get("parentID")
            padding = data.get("padding")
            newData = WorkspaceData()
            newData.text = text
            newData.parentID = parentID
            newData.padding = padding
            self.treeModel.updateWorkspace(id, newData)

        return updateWorkspace
