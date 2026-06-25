import json
import os

from src.app.events import Node
from src.app.state import Context
from src.router.routing import Dispatcher

from .model import ScriptModel, ScriptViewModel
from .service import ScriptService
from .ui import ScriptEditorController, ScriptManager


class ScriptComponent(Node):
    def __init__(self, context: Context, dispatcher: Dispatcher):
        super().__init__()

        self.context = context

        self.model = ScriptModel()
        self.viewModel = ScriptViewModel()
        self.editor = ScriptManager()

        self.controller = ScriptEditorController(
            self.editor, self.model, self.viewModel
        )

        self.subscribe("/App/Export", self.saveState)
        self.subscribe("/App/Reset", self.resetState)
        self.subscribe("/App/Import", self.loadState)

        self.service = ScriptService(self.model, self.viewModel, dispatcher)

    def saveState(self, data):
        path = data["path"]
        saveFile = os.path.join(path, "scripts.json")
        state = self.model.toData()
        with open(saveFile, "w") as f:
            json.dump(state, f, indent=4)

    def resetState(self, data):
        self.model.clear()

    def loadState(self, data):
        path = data["path"]
        saveFile = os.path.join(path, "scripts.json")
        state = None
        with open(saveFile, "r") as f:
            state = json.load(f)

        self.model.fromData(state)
