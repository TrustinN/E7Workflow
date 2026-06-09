from nanoid import generate

from src.app.frontend.events import Node
from src.app.frontend.state import WorkspaceContext

from .controller import WorkspaceController


class WorkspaceNode(Node):
    def __init__(self, context: WorkspaceContext, controller: WorkspaceController):
        super().__init__()
        self.context = context
        self.controller = controller

        self.availableGroups = set(chr(ord("A") + i) for i in range(26))

        self.subscribe("/Workspace/CreateRequested", self.createWorkspace)
        self.subscribe("/App/Loaded", self.createRootWorkspace)
        self.subscribe("/App/Reset", self.resetState)
        self.subscribe("/App/Import", self.importState)

    def popGroup(self):
        group = min(self.availableGroups)
        self.availableGroups.remove(group)
        return group

    def createRootWorkspace(self, data):
        id = generate()
        name = "Root"
        data = {
            "text": name,
            "id": id,
            "parentID": id,
            "grouping": None,
        }
        self.controller.createWorkspace(id, None, data)
        self.context.wsTreeModel.createRoot(id, data)
        self.context.wsGraphModel.createNode(id, data)
        self.context.selectionModel.setSelected(id)

    def createWorkspace(self, name):
        id = generate()
        parentID = self.context.selectionModel.getSelected()
        grouping = None
        if self.context.wsTreeModel.isRoot(parentID):
            grouping = self.popGroup()
        else:
            parentData = self.context.wsTreeModel.nodeData(parentID)
            grouping = parentData["grouping"]

        data = {
            "text": name,
            "id": id,
            "parentID": parentID,
            "grouping": grouping,
        }
        self.controller.createWorkspace(id, parentID, data)
        self.context.wsTreeModel.createNode(data["id"], data["parentID"], data)
        self.context.wsGraphModel.createNode(data["id"], data)

    def resetState(self, data):
        self.controller.clearState()
        self.availableGroups = set(chr(ord("A") + i) for i in range(26))

    def importState(self, data):
        self.controller.recreateView()
