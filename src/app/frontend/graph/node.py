from src.app.frontend.events import Node
from src.app.frontend.graph.mvc.model import GraphModel


class GraphNode(Node):
    def __init__(self, model: GraphModel):
        super().__init__()
        self.model = model

        self.subscribe("/WS Component/RootWSCreated", self.createNode)
        self.subscribe("/WS Component/WSCreated", self.createNode)
        # self.subscribe("/WS Component/WSFocused", self.setGraph)
        self.subscribe("/WS Component/WSExport", self.graphExport)
        self.subscribe("/WS Component/WSImport", self.graphImport)

    def createNode(self, data):
        self.model.createNode(data["id"], data)

    def createEdge(self, data):
        self.model.createEdge(data["id1"], data["id2"])

    def graphExport(self, data):
        self.serializer.export()

    def graphImport(self, data):
        self.serializer.restore()
