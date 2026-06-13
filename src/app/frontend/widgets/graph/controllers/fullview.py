from PyQt5.QtGui import QColor

from src.app.frontend.state import Context
from src.app.frontend.state.layouts.graph import Color
from src.app.frontend.widgets.graph.components import NodeSchema
from src.app.frontend.widgets.graph.views import GraphSingleView


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

    def setBorder(self, id, color: QColor):
        schema = NodeSchema(borderColor=Color(*color.getRgb()))
        self.view.updateNode(id, schema)

    def resetState(self):
        self.view.clearState()
