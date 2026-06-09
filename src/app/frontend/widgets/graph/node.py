import os

from src.app.frontend.events import Node
from src.app.frontend.state import GraphModel, Serializer, TreeModel, WorkspaceContext

from .controllers import GraphFullViewController, GraphMiniViewController


class GraphNode(Node):
    def __init__(
        self,
        context: WorkspaceContext,
        fullViewModel: GraphModel,
        miniViewModel: TreeModel,
        fullViewController: GraphFullViewController,
    ):
        super().__init__()
        self.context = context
        self.fullViewModel = fullViewModel
        self.miniViewModel = miniViewModel
        self.fullViewController = fullViewController
        self.serializer = Serializer()

        self.fullViewFile = "graph_full_view.json"
        self.miniViewFile = "graph_mini_view.json"

        self.subscribe("/Workspace/Created", self.createNode)
        self.subscribe("/Graph/EdgeRequested", self.createEdge)
        self.subscribe("/App/Reset", self.resetState)
        self.subscribe("/App/Export", self.graphExport)
        self.subscribe("/App/Import", self.graphImport)

        self.firstEdge = None
        self.secondEdge = None

    def createNode(self, data):
        nodeID = data["id"]

        if self.context.wsTreeModel.isRoot(nodeID):
            self.fullViewController.createGraph(nodeID)

        else:
            nodeData = self.context.wsGraphModel.getNodeData(nodeID)
            data = {"displayText": nodeData["grouping"]}
            self.fullViewController.createNode(nodeID)
            self.fullViewController.updateNode(nodeID, data)

    def setE1(self):
        self.firstEdge = self.context.selectionModel.getSelected()

    def setE2(self):
        self.secondEdge = self.context.selectionModel.getSelected()

    def createEdge(self):
        cond1 = self.firstEdge is not None
        cond2 = self.secondEdge is not None
        cond3 = self.firstEdge != self.secondEdge
        if cond1 and cond2 and cond3:
            self.fullViewController.createEdge(self.firstEdge, self.secondEdge)
            self.context.wsGraphModel.createEdge(self.firstEdge, self.secondEdge, {})
            self.firstEdge = None
            self.secondEdge = None

    def graphExport(self, data):
        path = data["path"]

        fullViewPath = os.path.join(path, self.fullViewFile)
        miniViewPath = os.path.join(path, self.miniViewFile)

        self.serializer.export(self.fullViewModel, fullViewPath)
        self.serializer.export(self.miniViewModel, miniViewPath)

    def graphImport(self, data):
        path = data["path"]

        fullViewPath = os.path.join(path, self.fullViewFile)
        miniViewPath = os.path.join(path, self.miniViewFile)

        fullViewModelState = self.serializer.restore(fullViewPath)
        miniViewModelState = self.serializer.restore(miniViewPath)

        self.fullViewModel.deserialize(fullViewModelState)
        self.miniViewModel.deserialize(miniViewModelState)

        self.fullViewController.recreateView()

    def resetState(self, data):
        self.firstEdge = None
        self.secondEdge = None
        self.fullViewController.clearState()
