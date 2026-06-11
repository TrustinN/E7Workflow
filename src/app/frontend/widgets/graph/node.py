import os

from src.app.frontend.events import Node
from src.app.frontend.state import GraphModel, Serializer, TreeModel, WorkspaceContext
from src.app.frontend.widgets.utils.colors import Colors

from .controllers import GraphFullViewController, GraphMiniViewController


class GraphNode(Node):
    def __init__(self, context: WorkspaceContext):
        super().__init__()
        self.context = context

        self.subscribe("/Workspace/Created", self.createNode)
        self.subscribe("/Graph/EdgeRequested", self.createEdge)
        self.subscribe("/App/Reset", self.resetState)

        self.firstEdge = None
        self.secondEdge = None

    def createNode(self, data):
        nodeID = data["id"]
        self.context.graphModel.createNode(nodeID, data)

    def setE1(self):
        self.firstEdge = self.context.selectionModel.getSelected()

    def setE2(self):
        self.secondEdge = self.context.selectionModel.getSelected()

    def createEdge(self, data):
        cond1 = self.firstEdge is not None
        cond2 = self.secondEdge is not None
        cond3 = self.firstEdge != self.secondEdge
        if cond1 and cond2 and cond3:
            self.context.graphModel.createEdge(self.firstEdge, self.secondEdge, {})
            self.firstEdge = None
            self.secondEdge = None

    def resetState(self, data):
        self.firstEdge = None
        self.secondEdge = None
