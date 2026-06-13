from src.app.frontend.state import Context
from src.app.frontend.widgets.graph.views import GraphSingleView
from src.app.frontend.widgets.utils.colors import Colors


class GraphFullViewController:
    def __init__(
        self,
        context: Context,
        view: GraphSingleView,
    ):
        self.context = context
        self.view = view

        self.context.selectionModel.selected_.connect(self.onSelectionChanged)
        self.context.runnerModel.selected_.connect(self.runnerSelectionChanged)

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

    def runnerSelectionChanged(self, id):
        prevID = self.context.runnerModel.getPrevSelected()
        if prevID:
            nodeData = {"borderColor": list(Colors.WHITE.getRgb())}
            self.view.updateNode(prevID, nodeData)

        nodeData = {"borderColor": list(Colors.MINT.getRgb())}
        self.view.updateNode(id, nodeData)

    def resetState(self):
        self.view.clearState()
