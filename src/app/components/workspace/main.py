import os

from PyQt5.QtWidgets import QApplication

from src.app.actions import ActionRegistry
from src.app.components.action.service import ActionRoute
from src.app.events import Node
from src.app.state import Context, SelectionType
from src.router.routing import Client, Dispatcher, Link

from .manager import WorkspaceManager
from .model import WorkspaceModel
from .service import WorkspaceService
from .ui import WorkspaceEditor, WorkspaceItemModel, WorkspaceTreeView


class WorkspaceComponent(Node):
    def __init__(
        self, context: Context, actions: ActionRegistry, dispatcher: Dispatcher
    ):
        super().__init__()

        self.context = context

        self.model = WorkspaceModel()
        self.manager = WorkspaceManager(self.model)
        self.client = Client("Workspace Client", dispatcher)
        self.service = WorkspaceService(self.model, dispatcher)

        self.editor = WorkspaceEditor(self.context, self.model, actions)

        self.model.modelDeleted.connect(self.onDelete)
        self.model.modelUpdated.connect(self.onUpdate)

        self.itemModel = WorkspaceItemModel(self.model)
        self.display = WorkspaceTreeView(self.itemModel, self.context)

        self.subscribe("/App/Loaded", self.createRootWorkspace)
        self.subscribe("/App/Export", self.saveState)
        self.subscribe("/App/Reset", self.resetState)
        self.subscribe("/App/Import", self.loadState)

        self.subscribe("/Workspace/Create/Request", self.handleCreateRequest)
        self.subscribe("/Workspace/Delete/Request", self.handleDeleteRequest)

        self.subscribe("/Runner/Action/Set", self.onRunnerActionSet)
        self.subscribe("/Runner/Action/Unset", self.onRunnerActionUnset)
        self.subscribe("/Runner/Execute/Prepare", self.hideAllWorkspaces)
        self.subscribe("/Runner/Execute/Finished", self.showAllWorkspaces)

    def createRootWorkspace(self, data):
        id = self.manager.createWorkspace(name="Root", padding=15)
        schema = self.manager.getWorkspace(id)
        self.publish("/Workspace/Node/Created", schema.toData())

    def handleCreateRequest(self, data):
        selection = self.context.selectionModel.getSelected()
        if not (selection.id and selection.type is SelectionType.WORKSPACE):
            return
        parentID = selection.id

        parent = self.model.getItem(parentID)
        id = self.manager.createWorkspace(
            parent=parentID,
            geometry=parent.geometry.adjusted(15, 15, -15, -15),
        )
        schema = self.manager.getWorkspace(id)
        self.publish("/Workspace/Node/Created", schema.toData())

    def handleDeleteRequest(self, data):
        selection = self.context.selectionModel.getSelected()
        if not (selection.id and selection.type is SelectionType.WORKSPACE):
            return

        self.manager.deleteWorkspace(selection.id)

    def onRunnerActionSet(self, data):
        id = data["workspaceID"]
        actionID = data["actionID"]

        link = Link(ActionRoute.NAME, ActionRoute.ACTION, actionID)
        resp = self.client.get(link)

        self.model.updateItem(id, {"iconPath": resp["icon"]})

    def onRunnerActionUnset(self, data):
        id = data["workspaceID"]

        self.model.updateItem(id, {"iconPath": ""})

    def onDelete(self, id):
        self.publish("/Workspace/Node/Deleted", {"id": id})

    def onUpdate(self, id):
        schema = self.model.getItem(id)
        self.publish("/Workspace/Node/Updated", schema.toData())

    def hideAllWorkspaces(self, data):
        QApplication.processEvents()
        ids = self.model.workspaces()
        for id in ids:
            self.model.updateItem(id, {"visible": False, "locked": True})
        QApplication.processEvents()

    def showAllWorkspaces(self, data):
        ids = self.model.workspaces()
        for id in ids:
            self.model.updateItem(id, {"visible": True, "locked": False})

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
