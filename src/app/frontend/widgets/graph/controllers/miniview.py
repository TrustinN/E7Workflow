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

        self.view.nodeSelected_.connect(self.onNodeSelected)
        self.view.nodeDeselected_.connect(self.onNodeDeselected)

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

    def setBorder(self, id, color: QColor):
        schema = NodeSchema(borderColor=Color(*color.getRgb()))
        self.view.updateNode(id, schema)

    def resetState(self):
        self._updatingSelection = False
        self.view.clearState()
