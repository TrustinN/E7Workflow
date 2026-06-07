import os

from src.app.frontend.events import Node
from src.app.frontend.models import GraphModel, Serializer, TreeModel


class GraphNode(Node):
    def __init__(
        self, model: GraphModel, fullViewModel: GraphModel, miniViewModel: TreeModel
    ):
        super().__init__()
        self.model = model
        self.fullViewModel = fullViewModel
        self.miniViewModel = miniViewModel
        self.serializer = Serializer()

        self.modelFile = "graph_data.json"
        self.fullViewFile = "graph_full_view.json"
        self.miniViewFile = "graph_mini_view.json"

        self.subscribe("/WS Component/RootWSCreated", self.createNode)
        self.subscribe("/WS Component/WSCreated", self.createNode)
        self.subscribe("/App/Export", self.graphExport)
        self.subscribe("/App/Import", self.graphImport)

    def createNode(self, data):
        self.model.createNode(data["id"], data)

    def createEdge(self, data):
        self.model.createEdge(data["id1"], data["id2"])

    def graphExport(self, data):
        path = data["path"]

        modelPath = os.path.join(path, self.modelFile)
        fullViewPath = os.path.join(path, self.fullViewFile)
        miniViewPath = os.path.join(path, self.miniViewFile)

        self.serializer.export(self.model, modelPath)
        self.serializer.export(self.fullViewModel, fullViewPath)
        self.serializer.export(self.miniViewModel, miniViewPath)

    def graphImport(self, data):
        path = data["path"]

        modelPath = os.path.join(path, self.modelFile)
        fullViewPath = os.path.join(path, self.fullViewFile)
        miniViewPath = os.path.join(path, self.miniViewFile)

        modelState = self.serializer.restore(modelPath)
        fullViewModelState = self.serializer.restore(fullViewPath)
        miniViewModelState = self.serializer.restore(miniViewPath)

        self.model.deserialize(modelState)
        self.fullViewModel.deserialize(fullViewModelState)
        self.miniViewModel.deserialize(miniViewModelState)
