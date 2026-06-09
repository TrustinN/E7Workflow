from PyQt5.QtCore import pyqtSignal

from src.app.frontend.state import GraphModel, WorkspaceContext
from src.app.frontend.widgets.graph.components import GraphScene, NodeType

from .view import GraphView


class GraphFullView(GraphView):
    graphCreated_ = pyqtSignal(str)
    nodeCreated_ = pyqtSignal(str)
    nodeUpdated_ = pyqtSignal(str)
    edgeCreated_ = pyqtSignal(str, str)
    edgeUpdated_ = pyqtSignal(str, str)

    def __init__(
        self,
        context: WorkspaceContext,
        viewModel: GraphModel,
    ):
        super().__init__()
        self.context = context
        self.viewModel = viewModel

        self.context.wsGraphModel.nodeCreated_.connect(self.onNodeCreate)
        self.context.wsGraphModel.edgeCreated_.connect(self.onEdgeCreate)
        self.context.wsGraphModel.modelClear_.connect(self.clearState)

        self.context.selectionModel.selected_.connect(self.onSelectionChanged)

        self.graphCreated_.connect(self.viewModelGraphCreate)
        self.nodeCreated_.connect(self.viewModelNodeCreate)
        self.nodeUpdated_.connect(self.viewModelNodeUpdate)
        self.edgeCreated_.connect(self.viewModelEdgeCreate)
        self.edgeUpdated_.connect(self.viewModelEdgeUpdate)
        self.viewModel.modelReset_.connect(self.onViewModelReset)

    def onSelectionChanged(self, id):
        if id in self.scene.nodes:
            self.scene.selectNode(id)
        else:
            self.scene.clearSelection()

    def _createScene(self, id: str):
        scene = GraphScene()

        scene.nodeSelected_.connect(self.context.selectionModel.setSelected)
        scene.nodeDeselected_.connect(
            lambda: self.context.selectionModel.setSelected(id)
        )
        scene.nodeMoved_.connect(self.nodeUpdated_)
        scene.edgeMoved_.connect(self.edgeUpdated_)
        return scene

    def createGraph(self, graphID):
        scene = self._createScene(graphID)
        self.setScene(scene)
        self.graphCreated_.emit(graphID)

    def createNode(self, nodeID):
        self.scene.createNode(nodeID, NodeType.CIRCLE)
        self.nodeCreated_.emit(nodeID)

    def updateNode(self, nodeID, data):
        self.scene.updateNode(nodeID, data)
        self.nodeUpdated_.emit(nodeID)

    def onNodeCreate(self, nodeID: str):
        nodeData = self.context.wsGraphModel.getNodeData(nodeID)

        parentID = nodeData["parentID"]
        isRoot = parentID == nodeID
        if isRoot:
            self.createGraph(nodeID)
            return

        self.createNode(nodeID)
        self.updateNode(nodeID, {"displayText": nodeData["grouping"]})

    def onEdgeCreate(self, e1, e2):
        self.scene.createEdge(e1, e2)
        self.edgeCreated_.emit(e1, e2)

    def updateEdge(self, e1, e2, data):
        self.scene.updateEdge(e1, e2, data)
        self.edgeUpdated_.emit(e1, e2)

    def viewModelGraphCreate(self, graphID: str):
        self.viewModel.createNode(graphID, {})

    def viewModelNodeCreate(self, nodeID: str):
        nodeData = self.scene.readNode(nodeID)
        self.viewModel.createNode(nodeID, nodeData)

    def viewModelNodeUpdate(self, nodeID: str):
        nodeData = self.scene.readNode(nodeID)
        self.viewModel.updateNode(nodeID, nodeData)

    def viewModelEdgeCreate(self, edgeID1: str, edgeID2: str):
        edgeData = self.scene.readEdge(edgeID1, edgeID2)
        self.viewModel.createEdge(edgeID1, edgeID2, edgeData)

    def viewModelEdgeUpdate(self, edgeID1: str, edgeID2: str):
        edgeData = self.scene.readEdge(edgeID1, edgeID2)
        self.viewModel.updateEdge(edgeID1, edgeID2, edgeData)

    def onViewModelReset(self):
        for nodeID in self.viewModel.nodeIter():
            nodeData = self.context.wsGraphModel.getNodeData(nodeID)

            parentID = nodeData["parentID"]
            isRoot = parentID == nodeID
            if isRoot:
                continue

            renderData = self.viewModel.getNodeData(nodeID)
            self.updateNode(nodeID, renderData)

        for edgeID in self.viewModel.edgeIter():
            renderData = self.viewModel.getEdgeData(edgeID[0], edgeID[1])
            self.updateEdge(edgeID[0], edgeID[1], renderData)

    def clearState(self):
        self.scene.deleteLater()
        self.setScene(None)
