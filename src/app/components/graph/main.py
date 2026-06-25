import os

from src.app.components.workspace.model import WorkspaceSchema
from src.app.events import Node
from src.app.state import Context
from src.router.routing import Dispatcher

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
        self.service = GraphService(self.model, dispatcher)

        self.editor = GraphEditor(self.context, self.model)
        self.editor.requestEdge.connect(self.createEdge)

        self.subscribe("/Workspace/Root/Created", self.createNode)
        self.subscribe("/Workspace/Node/Created", self.createNode)

        self.subscribe("/App/Export", self.saveState)
        self.subscribe("/App/Reset", self.resetState)
        self.subscribe("/App/Import", self.loadState)

        self.subscribe("/Graph/UpdateNode", self.updateNode)

    def createNode(self, data):
        wksSchema = WorkspaceSchema.fromData(data)

        nodeID = self.manager.createNode(wksSchema)
        schema = self.model.getNode(nodeID)

        self.publish("/Graph/Node/Created", schema.toData())

    def createEdge(self, source: str, target: str):
        edgeID = self.manager.createEdge(source, target)
        schema = self.model.getEdge(edgeID)

        self.publish("/Graph/Edge/Created", schema.toData())

    def updateNode(self, data):
        id = data["id"]
        patch = data["patch"]
        self.editor.updateNode(id, patch)

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
