from nanoid import generate

from src.app.frontend.events import Node
from src.app.frontend.state import WorkspaceContext


class WorkspaceNode(Node):
    def __init__(self, context: WorkspaceContext):
        super().__init__()
        self.context = context

        self.availableGroups = set(chr(ord("A") + i) for i in range(26))

        self.subscribe("/App/Loaded", self.createRootWorkspace)
        self.subscribe("/App/Reset", self.resetState)

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
        self.publish(
            "/Workspace/CreateRootRequested",
            data,
        )

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
        self.publish(
            "/Workspace/CreateChildRequested",
            data,
        )

    def resetState(self, data):
        self.availableGroups = set(chr(ord("A") + i) for i in range(26))
