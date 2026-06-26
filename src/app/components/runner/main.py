import os

from src.app.events import Node
from src.app.state import Context, SelectionType
from src.router.routing import Client, Dispatcher

from .manager import RunnerManager
from .model import RunnerModel
from .runner import Runner
from .ui import RunnerEditor


class RunnerComponent(Node):
    def __init__(self, context: Context, dispatcher: Dispatcher):
        super().__init__()

        self.context = context
        self.client = Client("RunnerClient", dispatcher)

        self.model = RunnerModel()
        self.runner = Runner(self.model, self.client)
        self.manager = RunnerManager(self.model, self.client)

        self.editor = RunnerEditor()
        self.editor.requestActionSet.connect(self.setAction)
        self.editor.requestActionUnset.connect(self.unsetAction)
        self.editor.requestScriptSet.connect(self.setScript)
        self.editor.requestScriptUnset.connect(self.unsetScript)
        self.editor.requestEntrySet.connect(self.setEntry)
        self.editor.requestExecute.connect(self.runner.execute)

        self.subscribe("/App/Export", self.saveState)
        self.subscribe("/App/Reset", self.resetState)
        self.subscribe("/App/Import", self.loadState)

        self.subscribe("/Workspace/Node/Created", self.onWorkspaceCreate)
        self.subscribe("/Script/Updated", self.onScriptUpdate)

    def setAction(self):
        selection = self.context.selectionModel.getSelected()
        if not (selection.id and selection.type == SelectionType.WORKSPACE):
            return

        actionID = self.manager.setAction(selection.id)
        self.publish(
            "/Runner/Action/Set", {"workspaceID": selection.id, "actionID": actionID}
        )

    def unsetAction(self):
        selection = self.context.selectionModel.getSelected()
        if not (selection.id and selection.type == SelectionType.WORKSPACE):
            return

        self.manager.unsetAction(selection.id)
        self.publish("/Runner/Action/Unset", {"workspaceID": selection.id})

    def setScript(self):
        selection = self.context.selectionModel.getSelected()
        if not (selection.id and selection.type == SelectionType.EDGE):
            return

        scriptID = self.manager.setScript(selection.id)
        self.publish(
            "/Runner/Script/Set", {"edgeID": selection.id, "scriptID": scriptID}
        )

    def unsetScript(self):
        selection = self.context.selectionModel.getSelected()
        if not (selection.id and selection.type == SelectionType.EDGE):
            return

        self.manager.unsetScript(selection.id)
        self.publish("/Runner/Script/Unset", {"edgeID": selection.id})

    def setEntry(self):
        selection = self.context.selectionModel.getSelected()
        if not (selection.id and selection.type == SelectionType.WORKSPACE):
            return

        prev = self.manager.setEntry(selection.id)
        self.publish("/Runner/Entry/Set", {"prevID": prev, "currID": selection.id})

    def onWorkspaceCreate(self, data):
        self.unsetAction()

    def onScriptUpdate(self, data):
        scriptID = data["id"]
        edges = self.model.edgesFromScript(scriptID)
        for edge in edges:
            self.publish(
                "/Runner/Script/Update", {"edgeID": edge, "scriptID": scriptID}
            )

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
