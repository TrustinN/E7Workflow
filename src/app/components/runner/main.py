import json
import os

from src.app.events import Node
from src.app.state import Context
from src.router.routing import Client, Dispatcher, Link

from .model import RunnerModel
from .runner import Runner


class RunnerComponent(Node):
    def __init__(self, context: Context, dispatcher: Dispatcher):
        super().__init__()

        self.context = context
        self.client = Client("RunnerClient", dispatcher)

        self.model = RunnerModel()
        self.runner = Runner(self.context, self.client)

        self.subscribe("/App/Export", self.saveState)
        self.subscribe("/App/Reset", self.resetState)
        self.subscribe("/App/Import", self.loadState)

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
