import os

from src.app.components.script.model import ScriptSchema
from src.app.components.utils.colors import Colors
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
        self.editor.requestActionUnset.connect(self.unsetAction)
        self.editor.requestScriptSet.connect(self.setScript)
        self.editor.requestEntrySet.connect(self.setEntry)
        self.editor.requestExecute.connect(self.runner.execute)

        self.subscribe("/App/Export", self.saveState)
        self.subscribe("/App/Reset", self.resetState)
        self.subscribe("/App/Import", self.loadState)

        self.subscribe("/Workspace/Node/Created", self.onWorkspaceCreate)
        self.subscribe("/Script/Updated", self.onScriptUpdate)

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

    def unsetAction(self):
        selection = self.context.selectionModel.getSelected()
        if not (selection.id and selection.type == SelectionType.WORKSPACE):
            return

        self.manager.unsetAction(selection.id)
        self.publish(
            "/Workspace/UpdateNode",
            {
                "id": selection.id,
                "patch": {"iconPath": ""},
            },
        )

    def setScript(self):
        selection = self.context.selectionModel.getSelected()
        if not (selection.id and selection.type == SelectionType.EDGE):
            return

        scriptID = self.manager.setScript(selection.id)
        schema = self.manager.getScript(scriptID)
        self.publish(
            "/Graph/UpdateEdge",
            {
                "id": selection.id,
                "patch": {"label": schema.name},
            },
        )

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

    def onWorkspaceCreate(self, data):
        self.unsetAction()

    def onScriptUpdate(self, data):
        id = data["id"]
        schema = ScriptSchema.fromData(data["schema"])
        edges = self.model.edgesFromScript(id)
        for edge in edges:
            self.publish(
                "/Graph/UpdateEdge",
                {
                    "id": edge,
                    "patch": {"label": schema.name},
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
