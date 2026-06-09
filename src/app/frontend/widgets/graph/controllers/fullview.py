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

        self.root = None
        self._loading = False

        self.context.selectionModel.selected_.connect(self.onSelectionChanged)

        self.view.nodeUpdated_.connect(self.onNodeUpdate)
        self.view.edgeUpdated_.connect(self.onEdgeUpdate)

        self.view.nodeSelected_.connect(self.onNodeSelected)
        self.view.nodeDeselected_.connect(self.onNodeDeselected)

    def _createGraph(self, id):
        self.view.createGraph(id)
        self.view.switchScene(id)
        self.root = id

    def createGraph(self, id):
        self._createGraph(id)
        self.viewModel.createNode(id, {})

    def _createNode(self, id):
        self.view.createNode(self.root, id, NodeType.CIRCLE)

    def createNode(self, id: str):
        self._createNode(id)
        nodeData = self.view.readNode(id, self.root)
        self.viewModel.createNode(id, nodeData)

    def _updateNode(self, id, data):
        self.view.updateNode(id, self.root, data)

    def updateNode(self, id: str, data):
        self._updateNode(id, data)
        self.onNodeUpdate(id)

    def _createEdge(self, e1, e2):
        self.view.createEdge(self.root, e1, e2)

    def createEdge(self, e1, e2):
        self._createEdge(e1, e2)
        edgeData = self.view.readEdge(e1, e2, self.root)
        self.viewModel.createEdge(e1, e2, edgeData)

    def onNodeSelected(self, id):
        self.context.selectionModel.setSelected(id)

    def onNodeDeselected(self):
        rootID = self.context.wsTreeModel.root
        self.context.selectionModel.setSelected(rootID)

    def onSelectionChanged(self, id):
        id = self.root if id == "" else id
        if id == self.root:
            self.view.clearSelection(id)
        else:
            self.view.selectNode(id, self.root)

    def onNodeUpdate(self, id: str):
        if self._loading:
            return

        nodeData = self.view.readNode(id, self.root)
        self.viewModel.updateNode(id, nodeData)

    def onEdgeUpdate(self, e1: str, e2: str):
        if self._loading:
            return

        edgeData = self.view.readEdge(e1, e2, self.root)
        self.viewModel.updateEdge(e1, e2, edgeData)

    def rerenderView(self):
        for nodeID in self.viewModel.nodeIter():
            if nodeID == self.root:
                continue

            data = self.viewModel.getNodeData(nodeID)
            self.view.updateNode(nodeID, self.root, data)

        for e1, e2 in self.viewModel.edgeIter():
            data = self.viewModel.getEdgeData(e1, e2)
            self.view.updateEdge(e1, e2, self.root, data)

    def recreateView(self):
        self._loading = True

        for nodeID in self.context.wsTreeModel.nodeIter():
            if self.context.wsTreeModel.isRoot(nodeID):
                self._createGraph(nodeID)
                continue

            self._createNode(nodeID)

        for e1, e2 in self.context.wsGraphModel.edgeIter():
            self._createEdge(e1, e2)

        self.rerenderView()

        self._loading = False

    def clearState(self):
        self.view.clearState()
        self.root = None
        self._loading = False
