from src.app.frontend.events import Node
from src.app.frontend.state import WorkspaceContext

from .controller import WorkspaceController
from .view import WorkspaceView


class WorkspaceComponent(Node):
    def __init__(self, context: WorkspaceContext):
        super().__init__()

        self.context = context

        self.view = WorkspaceView()
        self.controller = WorkspaceController(self.context, self.view)

        self.availableGroups = set(chr(ord("A") + i) for i in range(26))

        self.subscribe("/Workspace/CreateRootRequested", self.createRootWorkspace)
        self.subscribe("/Workspace/CreateRequested", self.createWorkspace)
        self.subscribe("/App/Reset", self.resetState)

    def popGroup(self):
        group = min(self.availableGroups)
        self.availableGroups.remove(group)
        return group

    def createRootWorkspace(self, data):
        id = data["id"]
        self.context.workspaceModel.createRoot(id, data)
        self.publish("/Workspace/Created", data)

        self.context.selectionModel.setSelected(id)

    def createWorkspace(self, data):
        id = data["id"]
        parentID = self.context.selectionModel.getSelected()
        grouping = None
        if self.context.workspaceModel.isRoot(parentID):
            grouping = self.popGroup()
        else:
            parentData = self.context.workspaceModel.nodeData(parentID)
            grouping = parentData["grouping"]

        data["grouping"] = grouping

        self.context.workspaceModel.createNode(id, parentID, data)
        self.publish("/Workspace/Created", data)

    def resetState(self, data):
        self.availableGroups = set(chr(ord("A") + i) for i in range(26))
