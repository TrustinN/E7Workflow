import json

from src.app.components.action.model import ActionSchema
from src.app.components.action.service import ActionRoute
from src.app.components.script.service import ScriptRoute
from src.router.routing import Client, Link

from .model import RunnerModel


class RunnerManager:
    def __init__(self, model: RunnerModel, client: Client):
        self.client = client
        self.model = model

    def setAction(self, nodeID: str) -> str:
        link = Link(ActionRoute.NAME, ActionRoute.CREATE)
        resp = self.client.post(link)
        actionID = resp["id"]
        self.model.setAction(nodeID, actionID)
        return actionID

    def getAction(self, actionID: str) -> ActionSchema:
        link = Link(ActionRoute.NAME, ActionRoute.ACTION, actionID)
        resp = self.client.get(link)
        return ActionSchema.fromData(resp)

    def setScript(self, edgeID: str) -> str:
        link = Link(ScriptRoute.NAME, ScriptRoute.SCRIPT)
        resp = self.client.get(link)
        scriptID = resp["id"]
        self.model.setScript(edgeID, scriptID)

    def setEntry(self, nodeID: str) -> str:
        prev = self.model.getEntry()
        self.model.setEntry(nodeID)
        return prev

    def saveModel(self, file):
        state = self.model.toData()
        with open(file, "w") as f:
            json.dump(state, f, indent=4)

    def resetModel(self):
        self.model.clear()

    def loadModel(self, file):
        with open(file, "r") as f:
            state = json.load(f)

            self.model.fromData(state)
