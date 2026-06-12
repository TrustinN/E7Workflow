from src.app.frontend.state import WorkspaceContext
from src.app.frontend.widgets.graph.components import NodeType
from src.app.frontend.widgets.graph.views import GraphSingleView
from src.app.frontend.widgets.utils.colors import Colors


class GraphFullViewController:
    def __init__(
        self,
        context: WorkspaceContext,
        view: GraphSingleView,
    ):
        self.context = context
        self.view = view

        self.context.graphModel.nodeCreated_.connect(self.createNodeOrGraph)
        self.context.graphModel.edgeCreated_.connect(self.createEdge)
        self.context.selectionModel.selected_.connect(self.onSelectionChanged)
        self.context.runnerModel.selected_.connect(self.runnerSelectionChanged)
        self.context.modelClear_.connect(self.clearState)
        self.context.modelLoaded_.connect(self.recreateView)

        self._loading = False

        self.view.nodeCreated_.connect(self.onNodeUpdate)
        self.view.edgeCreated_.connect(self.onEdgeUpdate)

        self.view.nodeUpdated_.connect(self.onNodeUpdate)
        self.view.edgeUpdated_.connect(self.onEdgeUpdate)

        self.view.nodeSelected_.connect(self.onNodeSelected)
        self.view.nodeDeselected_.connect(self.onNodeDeselected)

    def createGraph(self, id):
        self.view.createGraph(id)
        self.view.switchScene(id)

    def createNode(self, id):
        self.view.createNode(id, NodeType.CIRCLE)

        data = self.context.workspaceModel.nodeData(id)
        self.view.updateNode(id, {"displayText": data["grouping"]})

    def createNodeOrGraph(self, id):
        if self.context.workspaceModel.isRoot(id):
            self.createGraph(id)

        else:
            self.createNode(id)

    def createEdge(self, id):
        e1, e2 = self.context.graphModel.getEdge(id)
        self.view.createEdge(id, e1, e2)

    def updateNode(self, id, data):
        self.view.updateNode(id, data)

    def onNodeSelected(self, id):
        self.context.selectionModel.setSelected(id)

    def onNodeDeselected(self):
        rootID = self.context.workspaceModel.root
        self.context.selectionModel.setSelected(rootID)

    def onSelectionChanged(self, id):
        rootID = self.context.workspaceModel.root
        id = rootID if id == "" else id
        if id == rootID:
            self.view.clearSelection()
        else:
            self.view.selectNode(id)

    def runnerSelectionChanged(self, id):
        prevID = self.context.runnerModel.getPrevSelected()
        if prevID:
            nodeData = {"borderColor": list(Colors.WHITE.getRgb())}
            self.view.updateNode(prevID, nodeData)

        nodeData = {"borderColor": list(Colors.MINT.getRgb())}
        self.view.updateNode(id, nodeData)

    def onNodeUpdate(self, id: str):
        if self._loading:
            return

        data = self.context.graphModel.getNodeData(id)
        if "fullView" not in data:
            data["fullView"] = {}

        data["fullView"] = self.view.readNode(id)
        self.context.graphModel.updateNode(id, data)

    def onEdgeUpdate(self, id: str):
        if self._loading:
            return

        data = self.context.graphModel.getEdgeData(id)
        if "fullView" not in data:
            data["fullView"] = {}

        data["fullView"] = self.view.readEdge(id)
        self.context.graphModel.updateEdge(id, data)

    def rerenderView(self):
        for nodeID in self.context.workspaceModel.nodeIter():
            if self.context.workspaceModel.isRoot(nodeID):
                continue

            data = self.context.graphModel.getNodeData(nodeID)["fullView"]
            self.view.updateNode(nodeID, data)

        for edgeID in self.context.graphModel.edgeIter():
            data = self.context.graphModel.getEdgeData(edgeID)["fullView"]
            self.view.updateEdge(edgeID, data)

    def recreateView(self):
        self._loading = True

        for nodeID in self.context.workspaceModel.nodeIter():
            if self.context.workspaceModel.isRoot(nodeID):
                self.createGraph(nodeID)
                continue

            self.createNode(nodeID)

        for edgeID in self.context.graphModel.edgeIter():
            self.createEdge(edgeID)

        self.rerenderView()

        self._loading = False

    def clearState(self):
        self.view.clearState()
        self._loading = False
