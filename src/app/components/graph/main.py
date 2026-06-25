import json
import os

from nanoid import generate

from src.app.components.workspace.model import WorkspaceSchema
from src.app.events import Node
from src.app.state import Context
from src.router.routing import Dispatcher

from .model import EdgeSchema, GraphModel, NodeSchema
from .service import GraphService
from .ui.editor import GraphEditor


class GraphComponent(Node):

    def __init__(self, context: Context, dispatcher: Dispatcher):
        super().__init__()
        self.context = context
        self.model = GraphModel()
        self.editor = GraphEditor(self.context, self.model)
        self.editor.requestEdge.connect(self.createEdge)

        self.subscribe("/Workspace/Root/Created", self.createRoot)
        self.subscribe("/Workspace/Node/Created", self.createNode)

        self.subscribe("/App/Export", self.saveState)
        self.subscribe("/App/Reset", self.resetState)
        self.subscribe("/App/Import", self.loadState)

        self.service = GraphService(self.model, dispatcher)

    def createRoot(self, data):
        wksSchema = WorkspaceSchema.fromData(data)
        id = wksSchema.id
        schema = NodeSchema(id=id)

        self.model.addNode(id, schema)
        self.publish("/Graph/Root/Created", schema.toData())

    def createNode(self, data):
        wksSchema = WorkspaceSchema.fromData(data)
        id = wksSchema.id
        schema = NodeSchema(
            id=id,
            name=wksSchema.displayText,
            group=wksSchema.grouping,
            parent=wksSchema.parent,
        )

        self.model.addNode(id, schema)
        self.publish("/Graph/Node/Created", schema.toData())

    def createEdge(self, source, target):
        id = generate()

        schema = EdgeSchema(id=id, source=source, target=target)
        self.model.addEdge(id, schema)
        self.publish("/Graph/Edge/Created", schema.toData())

    def saveState(self, data):
        path = data["path"]
        saveFile = os.path.join(path, "graph.json")
        state = self.model.toData()
        with open(saveFile, "w") as f:
            json.dump(state, f, indent=4)

        self.editor.saveState(path)

    def resetState(self, data):
        self.model.clear()

    def loadState(self, data):
        path = data["path"]
        saveFile = os.path.join(path, "graph.json")
        state = None
        with open(saveFile, "r") as f:
            state = json.load(f)

        self.model.fromData(state)
        self.editor.loadState(path)
