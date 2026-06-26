import os

from src.app.components.action.service import ActionRoute
from src.app.events import Node
from src.app.state import Context
from src.router.routing import Client, Dispatcher, Link

from .manager import WorkspaceManager
from .model import WorkspaceModel
from .service import WorkspaceService
from .ui import WorkspaceEditor


class WorkspaceComponent(Node):
    def __init__(self, context: Context, dispatcher: Dispatcher):
        super().__init__()

        self.context = context

        self.model = WorkspaceModel()
        self.manager = WorkspaceManager(self.model)
        self.client = Client("Workspace Client", dispatcher)
        self.service = WorkspaceService(self.model, dispatcher)

        self.editor = WorkspaceEditor(self.context, self.model)
        self.editor.requestCreate.connect(self.createWorkspace)
        self.editor.requestDelete.connect(self.deleteWorkspace)

        self.model.modelDeleted.connect(self.onDelete)

        self.subscribe("/App/Loaded", self.createRootWorkspace)
        self.subscribe("/App/Export", self.saveState)
        self.subscribe("/App/Reset", self.resetState)
        self.subscribe("/App/Import", self.loadState)

        self.subscribe("/Runner/Action/Set", self.onRunnerActionSet)
        self.subscribe("/Runner/Action/Unset", self.onRunnerActionUnset)

    def createRootWorkspace(self, data):
        id = self.manager.createWorkspace(name="Root", padding=15)
        schema = self.manager.getWorkspace(id)
        self.publish("/Workspace/Root/Created", schema.toData())

    def createWorkspace(self, parent, name):
        id = self.manager.createWorkspace(name=name, parent=parent)
        schema = self.manager.getWorkspace(id)
        self.publish("/Workspace/Node/Created", schema.toData())

    def deleteWorkspace(self, id):
        self.manager.deleteWorkspace(id)

    def onDelete(self, id):
        self.publish("/Workspace/Node/Deleted", {"id": id})

    def onRunnerActionSet(self, data):
        id = data["workspaceID"]
        actionID = data["actionID"]

        link = Link(ActionRoute.NAME, ActionRoute.ACTION, actionID)
        resp = self.client.get(link)

        self.model.updateItem(id, {"iconPath": resp["icon"]})

    def onRunnerActionUnset(self, data):
        id = data["workspaceID"]

        self.model.updateItem(id, {"iconPath": ""})

    def saveState(self, data):
        path = data["path"]
        saveFile = os.path.join(path, "workspace.json")
        self.manager.saveModel(saveFile)

    def resetState(self, data):
        self.manager.resetModel()

    def loadState(self, data):
        path = data["path"]
        saveFile = os.path.join(path, "workspace.json")
        self.manager.loadModel(saveFile)
