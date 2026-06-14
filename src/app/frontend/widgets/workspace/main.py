from src.app.config import getIconPath
from src.app.frontend.events import Node
from src.app.frontend.state import Context, Document

from .builder import WorkspaceBuilder
from .controller import WorkspaceController
from .layout import WorkspaceLayoutSync
from .view import WorkspaceView


class WorkspaceComponent(Node):
    def __init__(self, context: Context, document: Document):
        super().__init__()

        self.context = context
        self.document = document

        self.view = WorkspaceView()

        self.builder = WorkspaceBuilder(self.context, self.view)
        self.layout = WorkspaceLayoutSync(self.document, self.view)
        self.controller = WorkspaceController(self.context, self.view)

        self.subscribe("/Workspace/Root/Requested", self.createRootWorkspace)
        self.subscribe("/Workspace/Requested", self.createWorkspace)

        self.subscribe("/Runner/Action/Set", self.setAction)
        self.subscribe("/Runner/Action/Unset", self.unsetAction)

        self.subscribe("/App/Reset", self.resetState)
        self.subscribe("/App/Import", self.loadState)

    def createRootWorkspace(self, data):
        id = data["id"]
        self.builder.createWorkspace(id)
        self.publish("/Workspace/Root/Created", data)

    def createWorkspace(self, data):
        id = data["id"]
        self.builder.createWorkspace(id)
        self.publish("/Workspace/Created", data)

    def setAction(self, data):
        id = data["id"]
        data = self.context.actionModel.getData(id)
        iconPath = getIconPath(data)
        self.controller.setIcon(id, iconPath)

    def unsetAction(self, data):
        id = data["id"]
        self.controller.setIcon(id, "")

    def resetState(self, data):
        self.layout.resetState()
        self.controller.resetState()

    def loadState(self, data):
        self.layout.freezeLayout()
        self.builder.buildAll()
        self.layout.rerenderView()
        self.layout.unfreezeLayout()
