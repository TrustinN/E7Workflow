from src.app.frontend.state import Context
from src.app.frontend.widgets.graph.components import NodeSchema
from src.app.frontend.widgets.graph.views import GraphMultiView


class GraphMiniViewBuilder:
    def __init__(
        self,
        context: Context,
        view: GraphMultiView,
    ):
        self.context = context
        self.view = view

    def createRoot(self, id):
        self.view.createGraph(id)
        self.view.switchScene(id)

    def createNode(self, id):
        parentID = self.context.workspaceModel.parent(id)

        self.view.createGraph(id)
        self.view.createNode(id, parentID)

        data = self.context.workspaceModel.nodeData(id)
        schema = NodeSchema(displayText=data["text"])

        self.view.updateNode(id, schema)

    def hasEdge(self, e1, e2):
        pe1 = self.context.workspaceModel.parent(e1)
        pe2 = self.context.workspaceModel.parent(e2)

        return pe1 == pe2

    def _createEdge(self, id, e1, e2):
        parentID = self.context.workspaceModel.parent(e1)
        self.view.createEdge(id, e1, e2, parentID)

    def createEdge(self, id):
        e1, e2 = self.context.graphModel.getEdge(id)
        if not self.hasEdge(e1, e2):
            return

        self._createEdge(id, e1, e2)

    def buildAll(self):
        for nodeID in self.context.workspaceModel.nodeIter():
            if self.context.workspaceModel.isRoot(nodeID):
                self.createRoot(nodeID)
                continue

            self.createNode(nodeID)

        for edgeID in self.context.graphModel.edgeIter():
            e1, e2 = self.context.graphModel.getEdge(edgeID)
            if not self.hasEdge(e1, e2):
                continue

            self._createEdge(edgeID, e1, e2)
