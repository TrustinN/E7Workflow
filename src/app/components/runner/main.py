import json
import os

from src.app.components.action.service import ActionRoute
from src.app.components.script.service import ScriptRoute
from src.app.events import Node
from src.app.state import Context, SelectionType
from src.router.routing import Client, Dispatcher, Link

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

        self.editor = RunnerEditor()
        self.editor.requestActionSet.connect(self.setAction)
        self.editor.requestScriptSet.connect(self.setScript)
        self.editor.requestEntrySet.connect(self.setEntry)
        self.editor.requestExecute.connect(self.runner.execute)

        self.subscribe("/App/Export", self.saveState)
        self.subscribe("/App/Reset", self.resetState)
        self.subscribe("/App/Import", self.loadState)

    def setAction(self):
        selection = self.context.selectionModel.getSelected()
        if not (selection.id and selection.type == SelectionType.WORKSPACE):
            return
        link = Link(ActionRoute.NAME, ActionRoute.CREATE)
        resp = self.client.post(link)
        self.model.setAction(selection.id, resp["id"])
        print(self.model.toData())

    def setScript(self):
        selection = self.context.selectionModel.getSelected()
        if not (selection.id and selection.type == SelectionType.EDGE):
            return
        link = Link(ScriptRoute.NAME, ScriptRoute.SCRIPT)
        resp = self.client.get(link)
        self.model.setScript(selection.id, resp["id"])
        print(self.model.toData())

    def setEntry(self):
        selection = self.context.selectionModel.getSelected()
        if not (selection.id and selection.type == SelectionType.WORKSPACE):
            return
        self.model.setEntry(selection.id)
        print(self.model.toData())

    def saveState(self, data):
        path = data["path"]
        saveFile = os.path.join(path, "runner.json")
        state = self.model.toData()
        with open(saveFile, "w") as f:
            json.dump(state, f, indent=4)

    def resetState(self, data):
        self.model.clear()

    def loadState(self, data):
        path = data["path"]
        saveFile = os.path.join(path, "runner.json")
        state = None
        with open(saveFile, "r") as f:
            state = json.load(f)

        self.model.fromData(state)
