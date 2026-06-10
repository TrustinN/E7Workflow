from src.app.backend.action import ActionRoute, ActionType
from src.app.frontend.events import Node
from src.app.frontend.state import WorkspaceContext
from src.router.routing import Client, Dispatcher, Link


class RunnerNode(Node):
    def __init__(
        self,
        context: WorkspaceContext,
        dispatcher: Dispatcher,
    ):
        super().__init__()
        self.context = context

        self.client = Client("RunnerClient", dispatcher)
        self.actionBindings = {}

        self.subscribe("/App/Reset", self.resetState)
        self.subscribe("/Runner/EntryRequested", self.setDefaultEntry)
        self.subscribe("/Runner/ExecuteRequested", self.execute)

        self.entryID = None

    def setDefaultEntry(self, data):
        entryID = self.context.selectionModel.getSelected()
        if self.context.wsTreeModel.isRoot(entryID):
            return

        prevID = self.entryID
        self.entryID = entryID
        self.publish("/Runner/EntrySet", {"prevID": prevID, "curID": entryID})

    def _executeNode(self, nodeID):
        if self.context.wsTreeModel.isLeaf(nodeID):
            if nodeID not in self.actionBindings:
                return  # no action binding

            actionData = self.actionBindings[nodeID]
            viewData = self.context.viewModel.nodeData(nodeID)
            geometry = viewData["geometry"]
            actionData["systemParams"] = {
                "tl": geometry[0],
                "br": geometry[1],
            }

            link = Link(ActionRoute.NAME, ActionRoute.ACTION, actionData["name"])
            self.client.post(
                link,
                actionData,
            )
            return

        edges = self.context.wsGraphModel.getEdges(nodeID)
        for node in edges:
            self._executeNode(node)

    def execute(self, data):
        if self.entryID is None:
            return

        self._executeNode(self.entryID)

    def setAction(self, data):
        if not self.context.selectionModel.hasSelected():
            return

        selection = self.context.selectionModel.getSelected()
        if self.context.wsTreeModel.isRoot(selection):
            return

        self.actionBindings[selection] = data

    def resetState(self, data):
        self.entryID = None
        pass
