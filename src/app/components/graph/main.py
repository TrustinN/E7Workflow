from src.app.components.workspace.model import WorkspaceSchema
from src.app.events import Node
from src.app.state import Context

from .model import GraphModel, NodeSchema
from .ui.editor import GraphEditor


class GraphComponent(Node):

    def __init__(self, context: Context):
        super().__init__()
        self.context = context
        self.model = GraphModel()
        self.editor = GraphEditor(self.context, self.model)

        self.subscribe("/Workspace/Root/Created", self.createRoot)
        self.subscribe("/Workspace/Node/Created", self.createNode)
        # self.subscribe("/Graph/Edge/Requested", self.createEdge)

        self.subscribe("/App/Reset", self.resetState)
        # self.subscribe("/App/Import", self.loadState)

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

    # def createEdge(self, data):
    #     id = data["id"]
    #     self.miniViewBuilder.createEdge(id)
    #     self.fullViewBuilder.createEdge(id)
    #     self.publish("/Graph/Edge/Created", data)

    def resetState(self, data):
        self.miniViewLayout.resetState()
        self.miniViewController.resetState()

        self.fullViewLayout.resetState()
        self.fullViewController.resetState()

    # def loadState(self, data):
    #     self.miniViewLayout.freezeLayout()
    #     self.miniViewBuilder.buildAll()
    #     self.miniViewLayout.rerenderView()
    #     self.miniViewLayout.unfreezeLayout()
    #
    #     self.fullViewLayout.freezeLayout()
    #     self.fullViewBuilder.buildAll()
    #     self.fullViewLayout.rerenderView()
    #     self.fullViewLayout.unfreezeLayout()
