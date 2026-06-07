from nanoid import generate

from src.app.frontend.events import Node
from src.app.frontend.state import SelectionModel

from .mvc import TreeModel


class WorkspaceNode(Node):
    def __init__(self, model: TreeModel, selectionModel: SelectionModel):
        super().__init__()
        self.workspaceModel = model
        self.selectionModel = selectionModel

        self.subscribe("/App/Loaded", self.createRootWorkspace)

    def createRootWorkspace(self, data):
        id = generate()
        name = "Root"
        data = {
            "text": name,
            "id": id,
            "parentID": id,
        }
        self.workspaceModel.createNode(id, id, data)
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
