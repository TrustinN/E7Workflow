from nanoid import generate

from src.app.frontend.events import Node
from src.app.frontend.state import SelectionModel

from .mvc import TreeModel, TreeModelSerializer


class WorkspaceNode(Node):
    def __init__(
        self, model: TreeModel, viewModel: TreeModel, selectionModel: SelectionModel
    ):
        super().__init__()
        self.workspaceModel = model
        self.viewModel = viewModel
        self.selectionModel = selectionModel

        self.serializer = TreeModelSerializer()

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
        self.serializer.export(self.workspaceModel, "ws_data.json")
        self.serializer.export(self.viewModel, "ws_view.json")

    def workspaceImport(self, data):
        modelState = self.serializer.restore("ws_data.json")
        viewModelState = self.serializer.restore("ws_view.json")

        self.workspaceModel.deserialize(modelState)
        self.viewModel.deserialize(viewModelState)
