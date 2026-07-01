import os
import time

from src.app.actions import ActionRegistry
from src.app.events import Node
from src.app.state import Context, SelectionType
from src.router.routing import Client, Dispatcher

from .execution import ExecutionBuilder, ExecutionController
from .manager import RunnerManager
from .model import RunnerModel
from .ui import RunnerEditor


class RunnerComponent(Node):
    def __init__(
        self, context: Context, actions: ActionRegistry, dispatcher: Dispatcher
    ):
        super().__init__()

        self.context = context
        self.client = Client("RunnerClient", dispatcher)

        self.model = RunnerModel()
        self.builder = ExecutionBuilder(self.model, self.client)
        self.executionController = ExecutionController(self.client)
        self.executionController.executionFinished.connect(
            lambda: self.publish("/Runner/Execute/Finished")
        )

        self.manager = RunnerManager(self.model, self.client)
        self.editor = RunnerEditor(self.context, self.model, actions)

        self.subscribe("/App/Export", self.saveState)
        self.subscribe("/App/Reset", self.resetState)
        self.subscribe("/App/Import", self.loadState)

        self.subscribe("/Runner/Action/Set/Request", self.handleSetActionRequest)
        self.subscribe("/Runner/Action/Unset/Request", self.handleUnsetActionRequest)
        self.subscribe("/Runner/Script/Set/Request", self.handleSetScriptRequest)
        self.subscribe("/Runner/Script/Unset/Request", self.handleUnsetScriptRequest)
        self.subscribe("/Runner/Entry/Set/Request", self.handleSetEntryRequest)
        self.subscribe("/Runner/Execute/Request", self.handleExecuteRequest)

        self.subscribe("/Workspace/Node/Created", self.onWorkspaceCreate)
        self.subscribe("/Workspace/Node/Deleted", self.onWorkspaceDelete)
        self.subscribe("/Graph/Edge/Deleted", self.onEdgeDelete)
        self.subscribe("/Graph/Edge/Created", self.onEdgeCreate)
        self.subscribe("/Script/Updated", self.onScriptUpdate)

    def handleSetActionRequest(self, data):
        selection = self.context.selectionModel.getSelected()
        if not (selection.id and selection.type == SelectionType.WORKSPACE):
            return

        actionID = self.manager.setAction(selection.id)
        self.publish(
            "/Runner/Action/Set", {"workspaceID": selection.id, "actionID": actionID}
        )

    def clearAction(self, workspaceID):
        self.manager.unsetAction(workspaceID)
        self.publish("/Runner/Action/Unset", {"workspaceID": workspaceID})

    def handleUnsetActionRequest(self, data):
        selection = self.context.selectionModel.getSelected()
        if not (selection.id and selection.type == SelectionType.WORKSPACE):
            return

        self.clearAction(selection.id)

    def handleSetScriptRequest(self, data):
        selection = self.context.selectionModel.getSelected()
        if not (selection.id and selection.type == SelectionType.EDGE):
            return

        scriptID = self.manager.setScript(selection.id)
        if scriptID is None:
            return
        self.publish(
            "/Runner/Script/Set", {"edgeID": selection.id, "scriptID": scriptID}
        )

    def handleUnsetScriptRequest(self, data):
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

    def handleSetEntryRequest(self, data):
        selection = self.context.selectionModel.getSelected()
        if not (selection.id and selection.type == SelectionType.WORKSPACE):
            return

        prev = self.manager.setEntry(selection.id)
        self.publish("/Runner/Entry/Set", {"prevID": prev, "currID": selection.id})

    def handleExecuteRequest(self, data):
        self.publish("/Runner/Execute/Prepare")
        time.sleep(0.3)

        context = self.builder.getContext()
        graph = self.builder.createGraph()
        self.executionController.executeGraph.emit(graph, context)

    def onWorkspaceCreate(self, data):
        if data["parent"]:
            self.clearAction(data["parent"])
        self.manager.createNode(data["id"])

    def onWorkspaceDelete(self, data):
        id = data["id"]
        self.manager.unsetAction(id)

        if id == self.model.getEntry():
            self.manager.unsetEntry()

    def onEdgeDelete(self, data):
        edgeID = data["edgeID"]
        self.manager.unsetScript(edgeID)

    def onEdgeCreate(self, data):
        edgeID = data["id"]
        self.manager.createScript(edgeID)

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
