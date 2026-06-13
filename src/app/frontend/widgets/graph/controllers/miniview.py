from src.app.frontend.state import Context
from src.app.frontend.widgets.graph.views import GraphMultiView
from src.app.frontend.widgets.utils.colors import Colors


class GraphMiniViewController:
    def __init__(
        self,
        context: Context,
        view: GraphMultiView,
    ):
        self.context = context
        self.view = view

        self.context.selectionModel.selected_.connect(self.onExternalSelection)
        self.context.runnerModel.selected_.connect(self.runnerSelectionChanged)

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

    def runnerSelectionChanged(self, id):
        prevID = self.context.runnerModel.getPrevSelected()
        if prevID:
            nodeData = {"borderColor": list(Colors.WHITE.getRgb())}
            parentID = self.context.workspaceModel.parent(prevID)
            self.view.updateNode(prevID, parentID, nodeData)

        nodeData = {"borderColor": list(Colors.MINT.getRgb())}
        parentID = self.context.workspaceModel.parent(id)
        self.view.updateNode(id, parentID, nodeData)

    def resetState(self):
        self._updatingSelection = False
        self.view.clearState()
