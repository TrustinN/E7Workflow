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

        self.context.wsGraphModel.modelClear_.connect(self.clearState)

        self.context.selectionModel.selected_.connect(self.onExternalSelection)
        self._updatingSelection = False
        self._loading = False

        self.view.nodeUpdated_.connect(self.onNodeUpdate)
        self.view.edgeUpdated_.connect(self.onEdgeUpdate)

        self.view.nodeSelected_.connect(self.onNodeSelected)
        self.view.nodeDeselected_.connect(self.onNodeDeselected)

    def _createRoot(self, id):
        self.view.createGraph(id)
        self.view.switchScene(id)

    def createRoot(self, id):
        self._createRoot(id)
        self.viewModel.createRoot(id, {})

    def _createNode(self, id):
        parentID = self.context.wsTreeModel.parent(id)

        self.view.createGraph(id)
        self.view.createNode(parentID, id)

    def createNode(self, id):
        self._createNode(id)

        parentID = self.context.wsTreeModel.parent(id)
        data = self.view.readNode(id, parentID)
        data["edges"] = {}
        self.viewModel.createNode(id, parentID, data)

    def updateNode(self, id, data):
        parentID = self.context.wsTreeModel.parent(id)
        self.view.updateNode(id, parentID, data)

    def _createEdge(self, e1, e2):
        pe1 = self.viewModel.parent(e1)
        pe2 = self.viewModel.parent(e2)

        if pe1 != pe2:
            return False

        self.view.createEdge(pe1, e1, e2)
        return True

    def createEdge(self, e1, e2):
        success = self._createEdge(e1, e2)
        if not success:
            return
        self.onEdgeUpdate(e1, e2)

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

    def onNodeUpdate(self, nodeID):
        if self._loading:
            return

        parentID = self.viewModel.parent(nodeID)

        data = self.view.readNode(nodeID, parentID)
        nodeData = self.viewModel.nodeData(nodeID)
        nodeData.update(data)

        self.viewModel.updateNode(nodeID, nodeData)

    def onEdgeUpdate(self, e1, e2):
        if self._loading:
            return

        parentID = self.context.wsTreeModel.parent(e1)
        data = self.view.readEdge(e1, e2, parentID)
        nodeData = self.viewModel.nodeData(e1)
        nodeData["edges"][e2] = data
        self.viewModel.updateNode(e1, nodeData)

    def rerenderView(self):
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

    def recreateView(self):
        self._loading = True

        for nodeID in self.viewModel.nodeIter():
            if self.viewModel.isRoot(nodeID):
                self._createRoot(nodeID)
                continue

            self._createNode(nodeID)

        for e1, e2 in self.context.wsGraphModel.edgeIter():
            self._createEdge(e1, e2)

        self.rerenderView()

        self._loading = False

    def clearState(self):
        self._loading = False
        self._updatingSelection = False
        self.view.clearState()
