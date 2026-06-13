from nanoid import generate

from src.app.frontend.events import Node
from src.app.frontend.state import Context


class WorkspaceCapability(Node):
    def __init__(self, context: Context):
        super().__init__()
        self.context = context

        self.availableGroups = set(chr(ord("A") + i) for i in range(26))
        self.groupAssignments = {}

        self.subscribe("/App/Loaded", self.createRootWorkspace)
        self.subscribe("/App/Reset", self.resetState)
        self.subscribe("/App/Import", self.loadState)

    def popGroup(self):
        group = min(self.availableGroups)
        self.availableGroups.remove(group)
        return group

    def assignGroup(self, id, parentID):
        group = None
        if self.context.workspaceModel.isRoot(parentID):
            group = self.popGroup()
            self.groupAssignments[id] = group

        else:
            group = self.groupAssignments[parentID]
            self.groupAssignments[id] = group

        return group

    def createRootWorkspace(self, data):
        id = generate()
        name = "Root"
        data = {
            "text": name,
            "id": id,
        }
        self.context.workspaceModel.createRoot(id, data)
        self.publish("/Workspace/CreateRootRequested", data)

    def createWorkspace(self, name):
        id = generate()
        parentID = self.context.selectionModel.getSelected()
        group = self.assignGroup(id, parentID)
        data = {
            "text": name,
            "id": id,
            "grouping": group,
        }
        self.context.workspaceModel.createNode(id, parentID, data)
        self.publish("/Workspace/CreateRequested", data)

    def loadState(self, data):
        for nodeID in self.context.workspaceModel.nodeIter():
            if self.context.workspaceModel.isRoot(nodeID):
                continue

            grouping = self.context.workspaceModel.nodeData(nodeID)["grouping"]
            self.groupAssignments[nodeID] = grouping
            self.availableGroups.discard(grouping)

    def resetState(self, data):
        self.availableGroups = set(chr(ord("A") + i) for i in range(26))
        self.groupAssignments = {}
