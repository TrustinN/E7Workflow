import os

from src.app.events import Node
from src.app.state import Context, SelectionType
from src.router.routing import Dispatcher

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
        self.service = WorkspaceService(self.model, dispatcher)

        self.editor = WorkspaceEditor(self.context, self.model)
        self.editor.requestWorkspace.connect(self.createWorkspace)

        self.subscribe("/App/Loaded", self.createRootWorkspace)
        self.subscribe("/App/Export", self.saveState)
        self.subscribe("/App/Reset", self.resetState)
        self.subscribe("/App/Import", self.loadState)

        self.subscribe("/Workspace/UpdateNode", self.updateWorkspace)

    def createRootWorkspace(self, data):
        id = self.manager.createWorkspace(name="Root", padding=15)
        schema = self.model.getItem(id)
        self.publish("/Workspace/Root/Created", schema.toData())

    def createWorkspace(self, name):
        selection = self.context.selectionModel.getSelected()
        if not (selection.id and selection.type is SelectionType.WORKSPACE):
            return

        id = self.manager.createWorkspace(name=name, parent=selection.id)
        schema = self.model.getItem(id)
        self.publish("/Workspace/Node/Created", schema.toData())

    def updateWorkspace(self, data):
        id = data["id"]
        patch = data["patch"]
        self.model.updateItem(id, patch)

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
