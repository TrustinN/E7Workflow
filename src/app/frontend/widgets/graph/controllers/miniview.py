from src.app.frontend.state import TreeModel, WorkspaceContext
from src.app.frontend.widgets.graph.views import GraphMultiView


class GraphMiniViewController:
    def __init__(
        self,
        context: WorkspaceContext,
        view: GraphMultiView,
        viewModel: TreeModel,
    ):
        self.context = context
        self.view = view
        self.viewModel = viewModel

        self.context.wsGraphModel.nodeCreated_.connect(self.onNodeCreate)
        self.context.wsGraphModel.edgeCreated_.connect(self.onEdgeCreate)
        self.context.wsGraphModel.modelClear_.connect(self.clearState)

        self.context.selectionModel.selected_.connect(self.onExternalSelection)
        self._updatingSelection = False

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
            self.viewModelRootCreate(nodeID)
            return

        parentID = self.context.wsTreeModel.parent(nodeID)

        self.view.createGraph(nodeID)
        self.view.createNode(parentID, nodeID)
        self.view.updateNode(nodeID, parentID, {"displayText": nodeData["text"]})

    def onEdgeCreate(self, e1, e2):
        pe1 = self.viewModel.parent(e1)
        pe2 = self.viewModel.parent(e2)

        if pe1 != pe2:
            return

        self.view.createEdge(pe1, e1, e2)

    def onExternalSelection(self, id):
        if self._updatingSelection:
            return

        prevID = self.context.selectionModel.getPrevSelected()
        if prevID:
            parentID = self.viewModel.parent(prevID)
            if parentID:
                self.view.unselectNode(prevID, parentID)

        rootID = self.context.wsTreeModel.root
        id = id or rootID
        self.view.switchScene(id)

    def onNodeSelected(self, id):
        if self._updatingSelection:
            return

        self._updatingSelection = True
        prevID = self.context.selectionModel.getPrevSelected()
        if prevID:
            parentID = self.viewModel.parent(prevID)
            if parentID:
                self.view.unselectNode(prevID, parentID)
        self.context.selectionModel.setSelected(id)
        self._updatingSelection = False

    def onNodeDeselected(self):
        if self._updatingSelection:
            return

        prevID = self.context.selectionModel.getPrevSelected()
        parentID = self.context.wsTreeModel.parent(prevID)
        self.context.selectionModel.setSelected(parentID)

    def viewModelRootCreate(self, nodeID):
        self.viewModel.createRoot(nodeID, {})

    def viewModelNodeCreate(self, nodeID, parentID):

        data = self.view.readNode(nodeID, parentID)
        data["edges"] = {}
        self.viewModel.createNode(nodeID, parentID, data)

    def viewModelEdgeCreate(self, e1, e2):
        self.viewModelEdgeUpdate(e1, e2)

    def viewModelNodeUpdate(self, nodeID):
        parentID = self.viewModel.parent(nodeID)

        data = self.view.readNode(nodeID, parentID)
        nodeData = self.viewModel.nodeData(nodeID)
        nodeData.update(data)

        self.viewModel.updateNode(nodeID, nodeData)

    def viewModelEdgeUpdate(self, e1, e2):
        parentID = self.context.wsTreeModel.parent(e1)
        data = self.view.readEdge(e1, e2, parentID)
        nodeData = self.viewModel.nodeData(e1)
        nodeData["edges"][e2] = data
        self.viewModel.updateNode(e1, nodeData)

    def onViewModelReset(self):
        for nodeID in self.viewModel.nodeIter():
            if self.viewModel.isRoot(nodeID):
                continue

            data = self.viewModel.nodeData(nodeID)
            parentID = self.context.wsTreeModel.parent(nodeID)
            self.view.updateNode(nodeID, parentID, data)

        for e1 in self.viewModel.nodeIter():
            nodeData = self.viewModel.nodeData(e1)

            parentID = self.context.wsTreeModel.parent(e1)
            edges = nodeData.get("edges", {})
            for e2, data in edges.items():
                self.view.updateEdge(e1, e2, parentID, data)

    def clearState(self):
        self.view.clearState()
