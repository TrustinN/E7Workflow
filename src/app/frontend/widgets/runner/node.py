from src.app.backend.action import ActionRoute
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

        self.subscribe("/Workspace/Created", self.unsetAction)
        self.subscribe("/Runner/EntryRequested", self.setDefaultEntry)
        self.subscribe("/Runner/ExecuteRequested", self.execute)

    def setDefaultEntry(self, data):
        entryID = self.context.selectionModel.getSelected()
        if self.context.workspaceModel.isRoot(entryID):
            return

        self.context.runnerModel.setSelected(entryID)

    def _executeNode(self, nodeID):
        if self.context.workspaceModel.isLeaf(nodeID):
            if not self.context.actionModel.hasKey(nodeID):
                return  # no action binding

            actionData = self.context.actionModel.getData(nodeID)
            data = self.context.workspaceModel.nodeData(nodeID)
            geometry = data["geometry"]
            actionData["systemParams"] = {
                "tl": geometry[0],
                "br": geometry[1],
            }

            link = Link(ActionRoute.NAME, ActionRoute.ACTION, actionData["name"])
            self.client.post(
                link,
                actionData,
            )

        edges = self.context.graphModel.getEdges(nodeID)
        for node in edges:
            self._executeNode(node)

    def execute(self, data):
        entryID = self.context.runnerModel.getSelected()
        print(entryID)
        if entryID is None:
            return

        self._executeNode(entryID)

    def setAction(self, data):
        if not self.context.selectionModel.hasSelected():
            return

        selection = self.context.selectionModel.getSelected()
        if self.context.workspaceModel.isRoot(selection):
            return

        if not self.context.workspaceModel.isLeaf(selection):
            return

        self.context.actionModel.setData(selection, data)

    def unsetAction(self, data):
        id = data["id"]
        parentID = self.context.workspaceModel.parent(id)
        if self.context.actionModel.hasKey(parentID):
            self.context.actionModel.delete(parentID)
