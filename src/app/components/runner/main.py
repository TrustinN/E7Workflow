import os

from src.app.components.utils.colors import Colors
from src.app.components.workspace.model import WorkspaceSchema
from src.app.events import Node
from src.app.state import Context, SelectionType
from src.router.routing import Client, Dispatcher

from .manager import RunnerManager
from .model import RunnerModel
from .runner import Runner
from .ui import RunnerEditor


class RunnerComponent(Node):
    def __init__(self, context: Context, dispatcher: Dispatcher):
        super().__init__()

        self.context = context
        self.client = Client("RunnerClient", dispatcher)

        self.model = RunnerModel()
        self.runner = Runner(self.model, self.client)
        self.manager = RunnerManager(self.model, self.client)

        self.editor = RunnerEditor()
        self.editor.requestActionSet.connect(self.setAction)
        self.editor.requestScriptSet.connect(self.setScript)
        self.editor.requestEntrySet.connect(self.setEntry)
        self.editor.requestExecute.connect(self.runner.execute)

        self.subscribe("/App/Export", self.saveState)
        self.subscribe("/App/Reset", self.resetState)
        self.subscribe("/App/Import", self.loadState)

        self.subscribe("/Workspace/Node/Created", self.onWorkspaceCreate)

    def setAction(self):
        selection = self.context.selectionModel.getSelected()
        if not (selection.id and selection.type == SelectionType.WORKSPACE):
            return

        actionID = self.manager.setAction(selection.id)
        if actionID is None:
            return

        schema = self.manager.getAction(actionID)
        self.publish(
            "/Workspace/UpdateNode",
            {
                "id": selection.id,
                "patch": {"iconPath": schema.icon},
            },
        )

    def unsetAction(self, id: str):
        self.manager.unsetAction(id)
        self.publish(
            "/Workspace/UpdateNode",
            {
                "id": id,
                "patch": {"iconPath": ""},
            },
        )

    def onWorkspaceCreate(self, data):
        schema = WorkspaceSchema.fromData(data)
        parent = schema.parent
        if parent:
            self.unsetAction(parent)

    def setScript(self):
        selection = self.context.selectionModel.getSelected()
        if not (selection.id and selection.type == SelectionType.EDGE):
            return

        self.manager.setScript(selection.id)

    def setEntry(self):
        selection = self.context.selectionModel.getSelected()
        if not (selection.id and selection.type == SelectionType.WORKSPACE):
            return

        prev = self.manager.setEntry(selection.id)
        if prev:
            self.publish(
                "/Graph/UpdateNode",
                {
                    "id": prev,
                    "patch": {
                        "borderColor": {
                            "r": Colors.WHITE.red(),
                            "g": Colors.WHITE.green(),
                            "b": Colors.WHITE.blue(),
                            "a": Colors.WHITE.alpha(),
                        }
                    },
                },
            )

        self.publish(
            "/Graph/UpdateNode",
            {
                "id": selection.id,
                "patch": {
                    "borderColor": {
                        "r": Colors.MINT.red(),
                        "g": Colors.MINT.green(),
                        "b": Colors.MINT.blue(),
                        "a": Colors.MINT.alpha(),
                    }
                },
            },
        )

    def saveState(self, data):
        path = data["path"]
        saveFile = os.path.join(path, "runner.json")
        self.manager.saveModel(saveFile)

    def resetState(self, data):
        self.manager.resetModel()

    def loadState(self, data):
        path = data["path"]
        saveFile = os.path.join(path, "runner.json")
        self.manager.loadModel(saveFile)
