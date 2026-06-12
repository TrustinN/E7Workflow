from src.app.frontend.state import WorkspaceContext
from src.app.frontend.widgets.graph.views import GraphMultiView
from src.app.frontend.widgets.utils.colors import Colors


class GraphMiniViewController:
    def __init__(
        self,
        context: WorkspaceContext,
        view: GraphMultiView,
    ):
        self.context = context
        self.view = view

        self.context.graphModel.nodeCreated_.connect(self.createNode)
        self.context.graphModel.edgeCreated_.connect(self.createEdge)
        self.context.selectionModel.selected_.connect(self.onExternalSelection)
        self.context.runnerModel.selected_.connect(self.runnerSelectionChanged)
        self.context.modelClear_.connect(self.clearState)
        self.context.modelLoaded_.connect(self.recreateView)

        self._updatingSelection = False
        self._loading = False

        self.view.nodeCreated_.connect(self.onNodeUpdate)
        self.view.edgeCreated_.connect(self.onEdgeUpdate)

        self.view.nodeUpdated_.connect(self.onNodeUpdate)
        self.view.edgeUpdated_.connect(self.onEdgeUpdate)

        self.view.nodeSelected_.connect(self.onNodeSelected)
        self.view.nodeDeselected_.connect(self.onNodeDeselected)

    def _createRoot(self, id):
        self.view.createGraph(id)
        self.view.switchScene(id)

    def _createChild(self, id, parentID):
        self.view.createGraph(id)
        self.view.createNode(id, parentID)

        data = self.context.workspaceModel.nodeData(id)
        self.view.updateNode(id, parentID, {"displayText": data["text"]})

    def createNode(self, id):
        parentID = self.context.workspaceModel.parent(id)

        if parentID is None:
            self._createRoot(id)

        else:
            self._createChild(id, parentID)

    def hasEdge(self, e1, e2):
        pe1 = self.context.workspaceModel.parent(e1)
        pe2 = self.context.workspaceModel.parent(e2)

        return pe1 == pe2

    def _createEdge(self, id, e1, e2):
        parentID = self.context.workspaceModel.parent(e1)
        self.view.createEdge(id, e1, e2, parentID)

    def createEdge(self, id):
        e1, e2 = self.context.graphModel.getEdge(id)
        if not self.hasEdge(e1, e2):
            return

        self._createEdge(id, e1, e2)

    def onExternalSelection(self, id):
        if self._updatingSelection:
            return

        prevID = self.context.selectionModel.getPrevSelected()
        if prevID:
            parentID = self.context.workspaceModel.parent(prevID)
            if parentID:
                self.view.unselectNode(prevID, parentID)

        rootID = self.context.workspaceModel.root
        id = id or rootID
        self.view.switchScene(id)

    def onNodeSelected(self, id):
        if self._updatingSelection:
            return

        self._updatingSelection = True
        prevID = self.context.selectionModel.getPrevSelected()
        if prevID:
            parentID = self.context.workspaceModel.parent(prevID)
            if parentID:
                self.view.unselectNode(prevID, parentID)
        self.context.selectionModel.setSelected(id)
        self._updatingSelection = False

    def onNodeDeselected(self):
        if self._updatingSelection:
            return

        id = self.context.selectionModel.getSelected()
        parentID = self.context.workspaceModel.parent(id)
        self.context.selectionModel.setSelected(parentID)

    def runnerSelectionChanged(self, id):
        prevID = self.context.runnerModel.getPrevSelected()
        if prevID:
            nodeData = {"borderColor": list(Colors.WHITE.getRgb())}
            parentID = self.context.workspaceModel.parent(prevID)
            self.view.updateNode(prevID, parentID, nodeData)

        nodeData = {"borderColor": list(Colors.MINT.getRgb())}
        parentID = self.context.workspaceModel.parent(id)
        self.view.updateNode(id, parentID, nodeData)

    def onNodeUpdate(self, id):
        if self._loading:
            return

        data = self.context.graphModel.getNodeData(id)

        if "miniView" not in data:
            data["miniView"] = {}

        parentID = self.context.workspaceModel.parent(id)
        data["miniView"] = self.view.readNode(id, parentID)

        self.context.graphModel.updateNode(id, data)

    def onEdgeUpdate(self, id):
        if self._loading:
            return

        data = self.context.graphModel.getEdgeData(id)
        e1, e2 = self.context.graphModel.getEdge(id)

        if "miniView" not in data:
            data["miniView"] = {}

        parentID = self.context.workspaceModel.parent(e1)
        data["miniView"] = self.view.readEdge(id, parentID)

        self.context.graphModel.updateEdge(id, data)

    def rerenderView(self):
        for nodeID in self.context.workspaceModel.nodeIter():
            if self.context.workspaceModel.isRoot(nodeID):
                continue

            parentID = self.context.workspaceModel.parent(nodeID)
            data = self.context.graphModel.getNodeData(nodeID)["miniView"]
            self.view.updateNode(nodeID, parentID, data)

        for id in self.context.graphModel.edgeIter():
            e1, e2 = self.context.graphModel.getEdge(id)
            if not self.hasEdge(e1, e2):
                continue

            parentID = self.context.workspaceModel.parent(e1)
            data = self.context.graphModel.getEdgeData(id)["miniView"]
            self.view.updateEdge(id, parentID, data)

    def recreateView(self):
        self._loading = True

        for nodeID in self.context.workspaceModel.nodeIter():
            self.createNode(nodeID)

        for edgeID in self.context.graphModel.edgeIter():
            e1, e2 = self.context.graphModel.getEdge(edgeID)
            if not self.hasEdge(e1, e2):
                continue

            self._createEdge(edgeID, e1, e2)

        self.rerenderView()

        self._loading = False

    def clearState(self):
        self._updatingSelection = False
        self._loading = False
        self.view.clearState()
