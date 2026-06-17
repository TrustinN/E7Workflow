from PyQt5.QtGui import QColor

from src.app.frontend.state import Context
from src.app.frontend.state.layouts.graph import Color
from src.app.frontend.widgets.graph.components import NodeSchema
from src.app.frontend.widgets.graph.views import GraphMultiView


class GraphMiniViewController:
    def __init__(
        self,
        context: Context,
        view: GraphMultiView,
    ):
        self.context = context
        self.view = view

        self.context.selectionModel.selected_.connect(self.onExternalSelection)

        self._updatingSelection = False

        self.view.nodeSelected_.connect(self.onItemSelected)
        self.view.nodeDeselected_.connect(self.onItemDeselected)

        self.view.edgeSelected_.connect(self.onItemSelected)
        self.view.edgeDeselected_.connect(self.onItemDeselected)

    def isEdge(self, id):
        for edgeID in self.context.graphModel.edgeIter():
            if edgeID == id:
                e1, e2 = self.context.graphModel.getEdge(id)
                parentID1 = self.context.workspaceModel.parent(e1)
                parentID2 = self.context.workspaceModel.parent(e2)
                if parentID1 == parentID2:
                    return True
                return False
        return False

    def isNode(self, id):
        for nodeID in self.context.graphModel.nodeIter():
            if nodeID == id:
                return True
        return False

    def unselectItem(self, id):
        if self.isNode(id):
            parentID = self.context.workspaceModel.parent(id)
            if parentID:
                self.view.unselectNode(id, parentID)
        elif self.isEdge(id):
            e1, e2 = self.context.graphModel.getEdge(id)
            parentID = self.context.workspaceModel.parent(e1)
            if parentID:
                self.view.unselectEdge(id, parentID)

    def onExternalSelection(self, id):
        if self._updatingSelection:
            return

        prevID = self.context.selectionModel.getPrevSelected()
        if prevID:
            self.unselectItem(prevID)

        if self.isNode(id):
            rootID = self.context.workspaceModel.root
            id = id or rootID
            self.view.switchScene(id)
        elif self.isEdge(id):
            e1, e2 = self.context.graphModel.getEdge(id)
            parentID = self.context.workspaceModel.parent(e1)
            self.view.selectEdge(id, parentID)

    def onItemSelected(self, id):
        if self._updatingSelection:
            return

        self._updatingSelection = True
        prevID = self.context.selectionModel.getPrevSelected()
        if prevID:
            self.unselectItem(prevID)

        self.context.selectionModel.setSelected(id)
        self._updatingSelection = False

    def onItemDeselected(self):
        if self._updatingSelection:
            return

        id = self.context.selectionModel.getSelected()
        parentID = None
        if self.isEdge(id):
            e1, e2 = self.context.graphModel.getEdge(id)
            parentID = self.context.workspaceModel.parent(e1)
        elif self.isNode(id):
            parentID = self.context.workspaceModel.parent(id)
        self.context.selectionModel.setSelected(parentID)

    def setBorder(self, id, color: QColor):
        schema = NodeSchema(borderColor=Color(*color.getRgb()))
        self.view.updateNode(id, schema)

    def resetState(self):
        self._updatingSelection = False
        self.view.clearState()
