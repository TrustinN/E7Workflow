import json
import os

from src.app.events import Node
from src.router.routing import Dispatcher

from .model import RuntimeModel
from .service import RuntimeService
from .ui import RuntimeEditor


class RuntimeComponent(Node):
    def __init__(self, dispatcher: Dispatcher):
        super().__init__()

        self.model = RuntimeModel()
        self.service = RuntimeService(self.model, dispatcher)

        self.editor = RuntimeEditor(self.model)

        self.subscribe("/App/Export", self.saveState)
        self.subscribe("/App/Reset", self.resetState)
        self.subscribe("/App/Import", self.loadState)

    def saveState(self, data):
        path = data["path"]
        saveFile = os.path.join(path, "runtime.json")
        state = self.model.toData()
        with open(saveFile, "w") as f:
            json.dump(state, f, indent=4)

    def resetState(self, data):
        self.model.clear()

    def loadState(self, data):
        path = data["path"]
        saveFile = os.path.join(path, "runtime.json")
        state = None
        with open(saveFile, "r") as f:
            state = json.load(f)

        self.model.fromData(state)
