import os

from src.app.actions import ActionRegistry
from src.app.events import Node
from src.app.state import Context, SelectionType
from src.router.routing import Client, Dispatcher

from .manager import RunnerManager
from .model import RunnerModel
from .runner import Runner
from .ui import RunnerEditor


class RunnerComponent(Node):
    def __init__(
        self, context: Context, actions: ActionRegistry, dispatcher: Dispatcher
    ):
        super().__init__()

        self.context = context
        self.client = Client("RunnerClient", dispatcher)

        self.model = RunnerModel()
        self.runner = Runner(self.model, self.client)
        self.manager = RunnerManager(self.model, self.client)

        self.editor = RunnerEditor(actions)

        self.subscribe("/App/Export", self.saveState)
        self.subscribe("/App/Reset", self.resetState)
        self.subscribe("/App/Import", self.loadState)

        self.subscribe("/Runner/Action/Set/Request", self.setAction)
        self.subscribe("/Runner/Action/Unset/Request", self.unsetAction)
        self.subscribe("/Runner/Script/Set/Request", self.setScript)
        self.subscribe("/Runner/Script/Unset/Request", self.unsetScript)
        self.subscribe("/Runner/Entry/Set/Request", self.setEntry)
        self.subscribe("/Runner/Execute/Request", self.execute)

        self.subscribe("/Workspace/Node/Created", self.onWorkspaceCreate)
        self.subscribe("/Workspace/Node/Deleted", self.onWorkspaceDelete)
        self.subscribe("/Graph/Edge/Deleted", self.onEdgeDelete)
        self.subscribe("/Script/Updated", self.onScriptUpdate)

    def setAction(self, data):
        selection = self.context.selectionModel.getSelected()
        if not (selection.id and selection.type == SelectionType.WORKSPACE):
            return

        actionID = self.manager.setAction(selection.id)
        self.publish(
            "/Runner/Action/Set", {"workspaceID": selection.id, "actionID": actionID}
        )

    def unsetAction(self, data):
        selection = self.context.selectionModel.getSelected()
        if not (selection.id and selection.type == SelectionType.WORKSPACE):
            return

        self.manager.unsetAction(selection.id)
        self.publish("/Runner/Action/Unset", {"workspaceID": selection.id})

    def setScript(self, data):
        selection = self.context.selectionModel.getSelected()
        if not (selection.id and selection.type == SelectionType.EDGE):
            return

        scriptID = self.manager.setScript(selection.id)
        self.publish(
            "/Runner/Script/Set", {"edgeID": selection.id, "scriptID": scriptID}
        )

    def unsetScript(self, data):
        selection = self.context.selectionModel.getSelected()
        if not (selection.id and selection.type == SelectionType.EDGE):
            return

        self.manager.unsetScript(selection.id)
        self.publish("/Runner/Script/Unset", {"edgeID": selection.id})

    def onScriptUpdate(self, data):
        scriptID = data["id"]
        edges = self.model.edgesFromScript(scriptID)
        for edge in edges:
            self.publish(
                "/Runner/Script/Updated", {"edgeID": edge, "scriptID": scriptID}
            )

    def setEntry(self, data):
        selection = self.context.selectionModel.getSelected()
        if not (selection.id and selection.type == SelectionType.WORKSPACE):
            return

        prev = self.manager.setEntry(selection.id)
        self.publish("/Runner/Entry/Set", {"prevID": prev, "currID": selection.id})

    def execute(self, data):
        self.runner.execute()

    def onWorkspaceCreate(self, data):
        self.unsetAction(data)

    def onWorkspaceDelete(self, data):
        id = data["id"]
        self.manager.unsetAction(id)

        if id == self.model.getEntry():
            self.manager.unsetEntry()

    def onEdgeDelete(self, data):
        edgeID = data["edgeID"]
        self.manager.unsetScript(edgeID)

    def saveState(self, data):
        path = data["path"]
        saveFile = os.path.join(path, "runner.json")
        self.manager.saveModel(saveFile)

    def resetState(self, data):
        self.manager.resetModel()

    def loadState(self, data):
        path = data["path"]
        saveFile = os.path.join(path, "runner.json")
        self.manager.loadModel(saveFile)
