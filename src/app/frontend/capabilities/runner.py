from nanoid import generate

from src.app.frontend.events import Node
from src.app.frontend.state import Context


class RunnerCapability(Node):
    def __init__(self, context: Context):
        super().__init__()
        self.context = context

        self.subscribe("/Runner/Action/Set/Requested", self.handleActionSetRequest)
        self.subscribe("/Runner/Action/Unset/Requested", self.handleActionUnsetRequest)
        self.subscribe("/Runner/Script/Model/Requested", self.handleScriptRequest)
        self.subscribe("/Runner/Script/Model/Set/Requested", self.handleScriptSet)
        self.subscribe("/Runner/Script/Model/Unset/Requested", self.handleScriptUnset)

    def handleActionSetRequest(self, data):
        if not self.context.selectionModel.hasSelected():
            return

        selection = self.context.selectionModel.getSelected()
        if selection not in self.context.workspaceModel.nodes():
            return

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
        if entryID not in self.context.workspaceModel.nodes():
            return

        if self.context.workspaceModel.isRoot(entryID):
            return

        self.context.runnerModel.setSelected(entryID)
        self.publish("/Runner/Entry/Set")

    def requestExecute(self):
        self.publish("/Runner/Execute/Requested")

    def handleScriptRequest(self, data):
        name = self.uniqueName("Untitled")
        id = generate()

        self.context.codeModel.setData(id, {"name": name, "code": ""})
        self.publish("/Runner/Script/Requested", {"id": id, "name": name})

    def handleScriptSet(self, data):
        selection = self.context.selectionModel.getSelected()
        if selection and selection in list(self.context.graphModel.edgeIter()):
            self.context.conditionalModel.setData(selection, data["scriptID"])

    def handleScriptUnset(self, data):
        selection = self.context.selectionModel.getSelected()
        if selection and selection in list(self.context.graphModel.edgeIter()):
            if selection in self.context.conditionalModel.keys():
                self.context.conditionalModel.delete(selection)

    def uniqueName(self, name):
        existing = {data["name"] for data in self.context.codeModel.values()}

        if name not in existing:
            return name

        i = 2
        while f"{name} ({i})" in existing:
            i += 1

        return f"{name} ({i})"
