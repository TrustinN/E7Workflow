from src.app.frontend.state import Context
from src.app.frontend.widgets.graph.components import NodeSchema, NodeType
from src.app.frontend.widgets.graph.views import GraphSingleView


class GraphFullViewBuilder:
    def __init__(
        self,
        context: Context,
        view: GraphSingleView,
    ):
        self.context = context
        self.view = view

    def createGraph(self, id):
        self.view.createGraph(id)
        self.view.switchScene(id)

    def createNode(self, id):
        self.view.createNode(id, NodeType.CIRCLE)

        data = self.context.workspaceModel.nodeData(id)
        schema = NodeSchema(displayText=data["grouping"])
        self.view.updateNode(id, schema)

    def createEdge(self, id):
        e1, e2 = self.context.graphModel.getEdge(id)
        self.view.createEdge(id, e1, e2)

    def buildAll(self):
        for nodeID in self.context.workspaceModel.nodeIter():
            if self.context.workspaceModel.isRoot(nodeID):
                self.createGraph(nodeID)
                continue

            self.createNode(nodeID)

        for edgeID in self.context.graphModel.edgeIter():
            self.createEdge(edgeID)
