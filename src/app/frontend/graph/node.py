import os

from src.app.frontend.events import Node
from src.app.frontend.graph.widgets import GraphButtons
from src.app.frontend.models import GraphModel, Serializer, TreeModel
from src.app.frontend.state import SelectionModel


class GraphNode(Node):
    def __init__(
        self,
        model: GraphModel,
        fullViewModel: GraphModel,
        miniViewModel: TreeModel,
        selectionModel: SelectionModel,
        buttons: GraphButtons,
    ):
        super().__init__()
        self.model = model
        self.fullViewModel = fullViewModel
        self.miniViewModel = miniViewModel
        self.selectionModel = selectionModel
        self.serializer = Serializer()

        self.modelFile = "graph_data.json"
        self.fullViewFile = "graph_full_view.json"
        self.miniViewFile = "graph_mini_view.json"

        self.subscribe("/WS Component/RootWSCreated", self.createNode)
        self.subscribe("/WS Component/WSCreated", self.createNode)
        self.subscribe("/App/Reset", self.resetState)
        self.subscribe("/App/Export", self.graphExport)
        self.subscribe("/App/Import", self.graphImport)

        self.buttons = buttons
        self.firstEdge = None
        self.secondEdge = None

        self.buttons.setE1Btn.clicked.connect(self.setE1)
        self.buttons.setE2Btn.clicked.connect(self.setE2)
        self.buttons.createEdgeBtn.clicked.connect(self.createEdge)

    def createNode(self, data):
        self.model.createNode(data["id"], data)

    def setE1(self):
        self.firstEdge = self.selectionModel.getSelected()

    def setE2(self):
        self.secondEdge = self.selectionModel.getSelected()

    def createEdge(self):
        cond1 = self.firstEdge is not None
        cond2 = self.secondEdge is not None
        cond3 = self.firstEdge != self.secondEdge
        if cond1 and cond2 and cond3:
            self.model.createEdge(self.firstEdge, self.secondEdge, {})
            self.publish(
                "/Graph/EdgeCreated", {"id1": self.firstEdge, "id2": self.secondEdge}
            )
            self.firstEdge = None
            self.secondEdge = None

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

    def resetState(self, data):
        self.firstEdge = None
        self.secondEdge = None
