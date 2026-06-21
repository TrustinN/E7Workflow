from PyQt5.QtGui import QColor

from src.app.components.graph.model import NodeSchema
from src.app.components.graph.views import GraphSingleView
from src.app.state import Context
from src.app.state.layouts.graph import Color


class GraphFullViewController:
    def __init__(
        self,
        context: Context,
        view: GraphSingleView,
    ):
        self.context = context
        self.view = view

        self.context.selectionModel.selected_.connect(self.onSelectionChanged)

        self.view.nodeSelected_.connect(self.onNodeSelected)
        self.view.nodeDeselected_.connect(self.onNodeDeselected)

        self.view.edgeSelected_.connect(self.onEdgeSelected)
        self.view.edgeDeselected_.connect(self.onEdgeDeselected)

    def updateNode(self, id, data):
        self.view.updateNode(id, data)

    def onNodeSelected(self, id):
        self.context.selectionModel.setSelected(id)

    def onNodeDeselected(self):
        rootID = self.context.workspaceModel.root
        self.context.selectionModel.setSelected(rootID)

    def onEdgeSelected(self, id):
        self.context.selectionModel.setSelected(id)

    def onEdgeDeselected(self):
        rootID = self.context.workspaceModel.root
        self.context.selectionModel.setSelected(rootID)

    def isEdge(self, id):
        for edgeID in self.context.graphModel.edgeIter():
            if edgeID == id:
                return True
        return False

    def isNode(self, id):
        for nodeID in self.context.graphModel.nodeIter():
            if nodeID == id:
                return True
        return False

    def onSelectionChanged(self, id):
        rootID = self.context.workspaceModel.root
        id = rootID if id == "" else id
        if id == rootID:
            self.view.clearSelection()
        elif self.isEdge(id):
            self.view.selectEdge(id)
        elif self.isNode(id):
            self.view.selectNode(id)

    def setBorder(self, id, color: QColor):
        schema = NodeSchema(borderColor=Color(*color.getRgb()))
        self.view.updateNode(id, schema)

    def resetState(self):
        self.view.clearState()
