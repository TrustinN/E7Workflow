from src.app.frontend.events import Node
from src.app.frontend.graph.mvc import GraphModel, GraphModelSerializer


class GraphNode(Node):
    def __init__(
        self, model: GraphModel, fullViewModel: GraphModel, miniViewModel: GraphModel
    ):
        super().__init__()
        self.model = model
        self.fullViewModel = fullViewModel
        self.miniViewModel = miniViewModel
        self.serializer = GraphModelSerializer()

        self.subscribe("/WS Component/RootWSCreated", self.createNode)
        self.subscribe("/WS Component/WSCreated", self.createNode)
        self.subscribe("/WS Component/WSClear", self.clearGraph)
        self.subscribe("/App/Export", self.graphExport)
        self.subscribe("/App/Import", self.graphImport)

    def createNode(self, data):
        self.model.createNode(data["id"], data)

    def createEdge(self, data):
        self.model.createEdge(data["id1"], data["id2"])

    def clearGraph(self, data):
        self.model.clear()

    def graphExport(self, data):
        self.serializer.export(self.model, "graph_data.json")
        self.serializer.export(self.fullViewModel, "graph_full_view.json")
        self.serializer.export(self.miniViewModel, "graph_mini_view.json")

    def graphImport(self, data):
        modelState = self.serializer.restore("graph_data.json")
        fullViewModelState = self.serializer.restore("graph_full_view.json")
        miniViewModelState = self.serializer.restore("graph_mini_view.json")

        self.model.deserialize(modelState)
        self.fullViewModel.deserialize(fullViewModelState)
        self.miniViewModel.deserialize(miniViewModelState)
