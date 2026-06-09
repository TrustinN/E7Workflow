from src.app.frontend.state import GraphModel, WorkspaceContext
from src.app.frontend.widgets.graph.components import NodeType
from src.app.frontend.widgets.graph.views import GraphMultiView


class GraphFullViewController:
    def __init__(
        self,
        context: WorkspaceContext,
        view: GraphMultiView,
        viewModel: GraphModel,
    ):
        self.context = context
        self.view = view
        self.viewModel = viewModel

        self.context.wsGraphModel.nodeCreated_.connect(self.onNodeCreate)
        self.context.wsGraphModel.edgeCreated_.connect(self.onEdgeCreate)
        self.context.wsGraphModel.modelClear_.connect(self.clearState)
        self.context.selectionModel.selected_.connect(self.onSelectionChanged)

        self.view.nodeCreated_.connect(self.viewModelNodeCreate)
        self.view.nodeUpdated_.connect(self.viewModelNodeUpdate)
        self.view.edgeCreated_.connect(self.viewModelEdgeCreate)
        self.view.edgeUpdated_.connect(self.viewModelEdgeUpdate)

        self.view.nodeSelected_.connect(self.onNodeSelected)
        self.view.nodeDeselected_.connect(self.onNodeDeselected)

        self.viewModel.modelReset_.connect(self.onViewModelReset)

    def onNodeCreate(self, nodeID: str):
        nodeData = self.context.wsGraphModel.getNodeData(nodeID)

        if self.context.wsTreeModel.isRoot(nodeID):
            self.view.createGraph(nodeID)
            self.view.switchScene(nodeID)
            self.viewModelGraphCreate(nodeID)
            return

        rootID = self.context.wsTreeModel.root
        self.view.createNode(rootID, nodeID, NodeType.CIRCLE)
        self.view.updateNode(nodeID, rootID, {"displayText": nodeData["grouping"]})

    def onEdgeCreate(self, e1, e2):
        rootID = self.context.wsTreeModel.root
        self.view.createEdge(rootID, e1, e2)

    def onNodeSelected(self, id):
        self.context.selectionModel.setSelected(id)

    def onNodeDeselected(self):
        rootID = self.context.wsTreeModel.root
        self.context.selectionModel.setSelected(rootID)

    def onSelectionChanged(self, id):
        id = self.context.wsTreeModel.root if id == "" else id
        if self.context.wsTreeModel.isRoot(id):
            self.view.clearSelection(id)
        else:
            rootID = self.context.wsTreeModel.root
            self.view.selectNode(id, rootID)

    def viewModelGraphCreate(self, graphID: str):
        self.viewModel.createNode(graphID, {})

    def viewModelNodeCreate(self, nodeID: str):
        rootID = self.context.wsTreeModel.root
        nodeData = self.view.readNode(nodeID, rootID)
        self.viewModel.createNode(nodeID, nodeData)

    def viewModelNodeUpdate(self, nodeID: str):
        rootID = self.context.wsTreeModel.root
        nodeData = self.view.readNode(nodeID, rootID)
        self.viewModel.updateNode(nodeID, nodeData)

    def viewModelEdgeCreate(self, edgeID1: str, edgeID2: str):
        rootID = self.context.wsTreeModel.root
        edgeData = self.view.readEdge(edgeID1, edgeID2, rootID)
        self.viewModel.createEdge(edgeID1, edgeID2, edgeData)

    def viewModelEdgeUpdate(self, edgeID1: str, edgeID2: str):
        rootID = self.context.wsTreeModel.root
        edgeData = self.view.readEdge(edgeID1, edgeID2, rootID)
        self.viewModel.updateEdge(edgeID1, edgeID2, edgeData)

    def onViewModelReset(self):
        for nodeID in self.viewModel.nodeIter():
            if self.context.wsTreeModel.isRoot(nodeID):
                continue

            rootID = self.context.wsTreeModel.root
            data = self.viewModel.getNodeData(nodeID)
            self.view.updateNode(nodeID, rootID, data)

        for e1, e2 in self.viewModel.edgeIter():
            rootID = self.context.wsTreeModel.root
            data = self.viewModel.getEdgeData(e1, e2)
            self.view.updateEdge(e1, e2, rootID, data)

    def clearState(self):
        self.view.clearState()
