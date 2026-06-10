import os

from nanoid import generate

from src.app.config import ICON_DIR
from src.app.frontend.events import Node
from src.app.frontend.state import WorkspaceContext

from .controller import WorkspaceController


class WorkspaceNode(Node):
    def __init__(self, context: WorkspaceContext, controller: WorkspaceController):
        super().__init__()
        self.context = context
        self.controller = controller

        self.availableGroups = set(chr(ord("A") + i) for i in range(26))
        self.iconPaths = {
            "Click": os.path.join(ICON_DIR, "mouse-pointer-click.svg"),
            "Drag.down": os.path.join(ICON_DIR, "move-down.svg"),
            "Drag.left": os.path.join(ICON_DIR, "move-left.svg"),
            "Drag.right": os.path.join(ICON_DIR, "move-right.svg"),
            "Drag.up": os.path.join(ICON_DIR, "move-up.svg"),
        }

        self.subscribe("/Workspace/CreateRequested", self.createWorkspace)
        self.subscribe("/Runner/ActionBind", self.onActionBind)
        self.subscribe("/Runner/ActionUnbind", self.onActionUnbind)
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

        self.publish("/Workspace/Created", data)

        self.context.selectionModel.setSelected(id)

    def createWorkspace(self, data):
        name = data["name"]
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

        self.publish("/Workspace/Created", data)

    def getIconPath(self, data):
        action = data["action"]
        name = action["name"]
        if name == "Click":
            return self.iconPaths[name]
        elif name == "Drag":
            userParams = action["userParams"]
            direction = userParams["dir"]["value"]
            return self.iconPaths[f"{name}.{direction}"]

    def onActionBind(self, data):
        id = data["id"]
        data = {"iconPath": self.getIconPath(data)}
        self.controller.updateWorkspace(id, data)

    def onActionUnbind(self, data):
        id = data["id"]
        data = {"iconPath": ""}
        self.controller.updateWorkspace(id, data)

    def resetState(self, data):
        self.controller.clearState()
        self.availableGroups = set(chr(ord("A") + i) for i in range(26))

    def importState(self, data):
        self.controller.recreateView()
