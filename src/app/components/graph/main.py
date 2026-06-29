import os

from src.app.actions import ActionRegistry
from src.app.components.script.service import ScriptRoute
from src.app.components.utils.colors import Colors
from src.app.components.workspace.model import WorkspaceSchema
from src.app.events import Node
from src.app.state import Context, SelectionType
from src.router.routing import Client, Dispatcher, Link

from .manager import GraphManager
from .model import GraphModel
from .service import GraphService
from .ui import GraphDisplay, GraphEditor


class GraphComponent(Node):

    def __init__(
        self, context: Context, actions: ActionRegistry, dispatcher: Dispatcher
    ):
        super().__init__()
        self.context = context

        self.model = GraphModel()
        self.manager = GraphManager(self.model)
        self.client = Client("Graph Client", dispatcher)
        self.service = GraphService(self.model, dispatcher)

        self.editor = GraphEditor(self.context, actions)
        self.display = GraphDisplay(self.context, self.model)

        self.model.edgeDeleted.connect(
            lambda id: self.publish("/Graph/Edge/Deleted", {"edgeID": id})
        )

        self.subscribe("/App/Export", self.saveState)
        self.subscribe("/App/Reset", self.resetState)
        self.subscribe("/App/Import", self.loadState)

        self.subscribe("/Graph/Edge/Create/Request", self.handleCreateEdgeRequest)
        self.subscribe("/Graph/Edge/SetStart/Request", lambda _: self.editor.setE1())
        self.subscribe("/Graph/Edge/SetEnd/Request", lambda _: self.editor.setE2())
        self.subscribe("/Graph/Edge/Delete/Request", self.handleDeleteEdgeRequest)

        self.subscribe("/Workspace/Node/Created", self.onWorkspaceCreated)
        self.subscribe("/Workspace/Node/Deleted", self.onWorkspaceDeleted)
        self.subscribe("/Workspace/Node/Updated", self.onWorkspaceUpdated)

        self.subscribe("/Runner/Entry/Set", self.onRunnerEntrySet)
        self.subscribe("/Runner/Script/Set", self.onRunnerScriptUpdate)
        self.subscribe("/Runner/Script/Updated", self.onRunnerScriptUpdate)
        self.subscribe("/Runner/Script/Unset", self.onRunnerScriptUnset)

    def onWorkspaceCreated(self, data):
        wksSchema = WorkspaceSchema.fromData(data)

        nodeID = self.manager.createNode(wksSchema)
        schema = self.model.getNode(nodeID)

        self.publish("/Graph/Node/Created", schema.toData())

    def onWorkspaceDeleted(self, data):
        id = data["id"]
        self.model.deleteNode(id)

    def onWorkspaceUpdated(self, data):
        wksSchema = WorkspaceSchema.fromData(data)
        self.model.updateNode(
            wksSchema.id, {"name": wksSchema.name, "group": wksSchema.grouping}
        )

    def handleCreateEdgeRequest(self, data):
        source, target = self.editor.draftEdge()
        if source is None or target is None:
            return
        edgeID = self.manager.createEdge(source, target)
        schema = self.model.getEdge(edgeID)

        self.publish("/Graph/Edge/Created", schema.toData())

    def handleDeleteEdgeRequest(self, data):
        selection = self.context.selectionModel.getSelected()
        if not (selection.id and selection.type == SelectionType.EDGE):
            return

        self.model.deleteEdge(selection.id)

    def onRunnerScriptUpdate(self, data):
        edgeID = data["edgeID"]
        scriptID = data["scriptID"]

        link = Link(ScriptRoute.NAME, ScriptRoute.SCRIPT, scriptID)
        resp = self.client.get(link)
        self.display.updateEdge(edgeID, {"label": resp["name"]})

    def onRunnerScriptUnset(self, data):
        edgeID = data["edgeID"]
        self.display.updateEdge(edgeID, {"label": ""})

    def onRunnerEntrySet(self, data):
        prevID = data["prevID"]
        currID = data["currID"]
        if prevID:
            self.display.updateNode(
                prevID,
                {
                    "borderColor": {
                        "r": Colors.WHITE.red(),
                        "g": Colors.WHITE.green(),
                        "b": Colors.WHITE.blue(),
                        "a": Colors.WHITE.alpha(),
                    }
                },
            )

        self.display.updateNode(
            currID,
            {
                "borderColor": {
                    "r": Colors.MINT.red(),
                    "g": Colors.MINT.green(),
                    "b": Colors.MINT.blue(),
                    "a": Colors.MINT.alpha(),
                }
            },
        )

    def saveState(self, data):
        path = data["path"]
        saveFile = os.path.join(path, "graph.json")
        self.manager.saveModel(saveFile)
        self.display.saveState(path)

    def resetState(self, data):
        self.manager.resetModel()

    def loadState(self, data):
        path = data["path"]
        saveFile = os.path.join(path, "graph.json")
        self.manager.loadModel(saveFile)
        self.display.loadState(path)
