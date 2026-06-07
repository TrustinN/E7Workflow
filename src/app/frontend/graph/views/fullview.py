from PyQt5.QtCore import pyqtSignal

from src.app.frontend.graph.components import GraphScene
from src.app.frontend.graph.widgets import GraphViewWidget
from src.app.frontend.models import GraphModel
from src.app.frontend.state import SelectionModel


class GraphFullView(GraphViewWidget):
    graphCreated_ = pyqtSignal(str)
    nodeCreated_ = pyqtSignal(str)

    def __init__(
        self,
        model: GraphModel,
        viewModel: GraphModel,
        selectionModel: SelectionModel,
    ):
        super().__init__()
        self.model = model
        self.viewModel = viewModel
        self.selectionModel = selectionModel

        self.model.nodeCreated_.connect(self.onNodeCreate)
        self.model.edgeCreated_.connect(self.onEdgeCreate)
        self.model.modelClear_.connect(self.clearState)

        self.selectionModel.selected_.connect(self.onSelectionChanged)

        self.graphCreated_.connect(self.viewModelGraphCreate)
        self.nodeCreated_.connect(self.viewModelNodeCreate)
        self.viewModel.modelReset_.connect(self.onViewModelReset)

    def onSelectionChanged(self, id):
        if id in self.scene.nodes:
            self.scene.selectNode(id)
        else:
            self.scene.clearSelection()

    def onGraphCreate(self, graphID: str):
        scene = GraphScene()

        if self.scene is None:
            self.setScene(scene)
            self.scene.nodeSelected_.connect(self.selectionModel.setSelected)
            self.scene.nodeDeselected_.connect(
                lambda: self.selectionModel.setSelected(graphID)
            )
            self.scene.nodeMoved_.connect(self.viewModelNodeUpdate)

        self.graphCreated_.emit(graphID)

    def onNodeCreate(self, nodeID: str):
        nodeData = self.model.getNodeData(nodeID)

        parentID = nodeData["parentID"]
        isRoot = parentID == nodeID
        if isRoot:
            self.onGraphCreate(nodeID)
            return

        self.scene.createNode(nodeID)
        self.scene.updateNode(nodeID, {"displayText": nodeData["text"]})

        self.nodeCreated_.emit(nodeID)

    def onEdgeCreate(self, edgeIDs: tuple[str, str]):
        pass

    def viewModelGraphCreate(self, graphID: str):
        self.viewModel.createNode(graphID, {})

    def viewModelNodeCreate(self, nodeID: str):
        nodeData = self.scene.readNode(nodeID)
        self.viewModel.createNode(nodeID, nodeData)

    def viewModelNodeUpdate(self, nodeID: str):
        nodeData = self.scene.readNode(nodeID)
        self.viewModel.updateNode(nodeID, nodeData)

    def onViewModelReset(self):
        for nodeID in self.viewModel.nodeIter():
            renderData = self.viewModel.getNodeData(nodeID)
            self.scene.updateNode(nodeID, renderData)

        for edgeID in self.viewModel.edgeIter():
            renderData = self.viewModel.getEdgeData(edgeID[0], edgeID[1])
            self.scene.updateEdge(edgeID[0], edgeID[1], renderData)

    def clearState(self):
        self.scene.deleteLater()
        self.setScene(None)
