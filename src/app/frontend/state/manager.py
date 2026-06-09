import os

from src.app.frontend.events import Node

from .models import Serializer
from .workspace import WorkspaceContext


class WorkspaceContextManager(Node):
    def __init__(self, context: WorkspaceContext):
        super().__init__()
        self.context = context

        self.serializer = Serializer()

        self.treeFile = "ws_data.json"
        self.graphFile = "graph_data.json"
        self.viewFile = "ws_view.json"

        self.subscribe("/Workspace/CreateRootRequested", self.onWSRootRequest)
        self.subscribe("/Workspace/CreateChildRequested", self.onWSChildRequest)
        self.subscribe("/Graph/CreateEdgeRequested", self.onGraphEdgeRequest)

        self.subscribe("/App/Reset", self.contextReset)
        self.subscribe("/App/Export", self.contextExport)
        self.subscribe("/App/Import", self.contextImport)

    def onWSRootRequest(self, data):
        self.context.wsTreeModel.createRoot(data["id"], data)
        self.context.wsGraphModel.createNode(data["id"], data)
        self.context.selectionModel.setSelected(data["id"])

    def onWSChildRequest(self, data):
        self.context.wsTreeModel.createNode(data["id"], data["parentID"], data)
        self.context.wsGraphModel.createNode(data["id"], data)

    def onGraphEdgeRequest(self, data):
        self.context.wsGraphModel.createEdge(data["id1"], data["id2"], {})

    def contextExport(self, data):
        path = data["path"]

        treePath = os.path.join(path, self.treeFile)
        graphPath = os.path.join(path, self.graphFile)
        viewPath = os.path.join(path, self.viewFile)

        self.serializer.export(self.context.wsTreeModel, treePath)
        self.serializer.export(self.context.wsGraphModel, graphPath)
        self.serializer.export(self.context.viewModel, viewPath)

    def contextImport(self, data):
        path = data["path"]

        treePath = os.path.join(path, self.treeFile)
        graphPath = os.path.join(path, self.graphFile)
        viewPath = os.path.join(path, self.viewFile)

        treeState = self.serializer.restore(treePath)
        graphState = self.serializer.restore(graphPath)
        viewState = self.serializer.restore(viewPath)

        self.context.wsTreeModel.deserialize(treeState)
        self.context.wsGraphModel.deserialize(graphState)
        self.context.viewModel.deserialize(viewState)

    def contextReset(self, data):
        self.context.selectionModel.reset()
