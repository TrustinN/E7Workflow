from src.app.frontend.events import Node
from src.app.frontend.state import Context


class RunnerCapability(Node):
    def __init__(self, context: Context):
        super().__init__()
        self.context = context

        self.subscribe("/Runner/Action/Set/Requested", self.handleActionSetRequest)
        self.subscribe("/Runner/Action/Unset/Requested", self.handleActionUnsetRequest)

    def handleActionSetRequest(self, data):
        if not self.context.selectionModel.hasSelected():
            return

        selection = self.context.selectionModel.getSelected()
        if self.context.workspaceModel.isRoot(selection):
            return

        if not self.context.workspaceModel.isLeaf(selection):
            return

        self.context.actionModel.setData(selection, data)

        self.publish("/Runner/Action/Set", {"id": selection})

    def handleActionUnsetRequest(self, data):
        id = data["id"]
        if self.context.actionModel.hasKey(id):
            self.context.actionModel.delete(id)

        self.publish("/Runner/Action/Unset", data)

    def requestEntry(self):
        entryID = self.context.selectionModel.getSelected()
        if self.context.workspaceModel.isRoot(entryID):
            return

        self.context.runnerModel.setSelected(entryID)
        self.publish("/Runner/Entry/Set")

    def requestExecute(self):
        self.publish("/Runner/Execute/Requested")
