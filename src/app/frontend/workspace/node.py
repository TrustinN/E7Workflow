import os

from nanoid import generate

from src.app.frontend.events import Node
from src.app.frontend.models import Serializer, TreeModel
from src.app.frontend.state import SelectionModel


class WorkspaceNode(Node):
    def __init__(
        self, model: TreeModel, viewModel: TreeModel, selectionModel: SelectionModel
    ):
        super().__init__()
        self.workspaceModel = model
        self.viewModel = viewModel
        self.selectionModel = selectionModel
        self.serializer = Serializer()

        self.modelFile = "ws_data.json"
        self.viewFile = "ws_view.json"

        self.subscribe("/App/Loaded", self.createRootWorkspace)
        self.subscribe("/App/Export", self.workspaceExport)
        self.subscribe("/App/Import", self.workspaceImport)

    def createRootWorkspace(self, data):
        id = generate()
        name = "Root"
        data = {
            "text": name,
            "id": id,
            "parentID": id,
        }
        self.workspaceModel.createRoot(id, data)
        self.publish(
            "/WS Component/RootWSCreated",
            data,
        )
        self.selectionModel.setSelected(id)

    def createWorkspace(self, name):
        id = generate()
        parentID = self.selectionModel.getSelected()
        data = {
            "text": name,
            "id": id,
            "parentID": parentID,
        }
        self.workspaceModel.createNode(id, parentID, data)
        self.publish(
            "/WS Component/WSCreated",
            data,
        )

    def workspaceExport(self, data):
        path = data["path"]

        modelPath = os.path.join(path, self.modelFile)
        viewPath = os.path.join(path, self.viewFile)

        self.serializer.export(self.workspaceModel, modelPath)
        self.serializer.export(self.viewModel, viewPath)

    def workspaceImport(self, data):
        path = data["path"]

        modelPath = os.path.join(path, self.modelFile)
        viewPath = os.path.join(path, self.viewFile)

        modelState = self.serializer.restore(modelPath)
        viewModelState = self.serializer.restore(viewPath)

        self.workspaceModel.deserialize(modelState)
        self.viewModel.deserialize(viewModelState)
