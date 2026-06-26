import os

from src.app.components.script.service import ScriptRoute
from src.app.components.utils.colors import Colors
from src.app.components.workspace.model import WorkspaceSchema
from src.app.events import Node
from src.app.state import Context
from src.router.routing import Client, Dispatcher, Link

from .manager import GraphManager
from .model import GraphModel
from .service import GraphService
from .ui import GraphEditor


class GraphComponent(Node):

    def __init__(self, context: Context, dispatcher: Dispatcher):
        super().__init__()
        self.context = context

        self.model = GraphModel()
        self.manager = GraphManager(self.model)
        self.client = Client("Graph Client", dispatcher)
        self.service = GraphService(self.model, dispatcher)

        self.editor = GraphEditor(self.context, self.model)
        self.editor.requestEdge.connect(self.createEdge)

        self.subscribe("/Workspace/Root/Created", self.createNode)
        self.subscribe("/Workspace/Node/Created", self.createNode)
        self.subscribe("/Workspace/Node/Deleted", self.deleteNode)

        self.subscribe("/App/Export", self.saveState)
        self.subscribe("/App/Reset", self.resetState)
        self.subscribe("/App/Import", self.loadState)

        self.subscribe("/Runner/Entry/Set", self.onRunnerEntrySet)
        self.subscribe("/Runner/Script/Set", self.onRunnerScriptUpdate)
        self.subscribe("/Runner/Script/Update", self.onRunnerScriptUpdate)
        self.subscribe("/Runner/Script/Unset", self.onRunnerScriptUnset)

    def createNode(self, data):
        wksSchema = WorkspaceSchema.fromData(data)

        nodeID = self.manager.createNode(wksSchema)
        schema = self.model.getNode(nodeID)

        self.publish("/Graph/Node/Created", schema.toData())

    def createEdge(self, source: str, target: str):
        edgeID = self.manager.createEdge(source, target)
        schema = self.model.getEdge(edgeID)

        self.publish("/Graph/Edge/Created", schema.toData())

    def onRunnerScriptUpdate(self, data):
        edgeID = data["edgeID"]
        scriptID = data["scriptID"]

        link = Link(ScriptRoute.NAME, ScriptRoute.SCRIPT, scriptID)
        resp = self.client.get(link)
        self.editor.updateEdge(edgeID, {"label": resp["name"]})

    def onRunnerScriptUnset(self, data):
        edgeID = data["edgeID"]
        self.editor.updateEdge(edgeID, {"label": ""})

    def onRunnerEntrySet(self, data):
        prevID = data["prevID"]
        currID = data["currID"]
        if prevID:
            self.editor.updateNode(
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

        self.editor.updateNode(
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
        pass

    def deleteNode(self, data):
        id = data["id"]
        self.model.deleteNode(id)

    def saveState(self, data):
        path = data["path"]
        saveFile = os.path.join(path, "graph.json")
        self.manager.saveModel(saveFile)
        self.editor.saveState(path)

    def resetState(self, data):
        self.manager.resetModel()

    def loadState(self, data):
        path = data["path"]
        saveFile = os.path.join(path, "graph.json")
        self.manager.loadModel(saveFile)
        self.editor.loadState(path)
