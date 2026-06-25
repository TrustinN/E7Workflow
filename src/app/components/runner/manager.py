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
        link = Link(ActionRoute.NAME, ActionRoute.ACTION)
        resp = self.client.get(link)
        return ActionSchema.fromData(resp)

    def setScript(self, edgeID: str) -> str:
        link = Link(ScriptRoute.NAME, ScriptRoute.SCRIPT)
        resp = self.client.get(link)
        scriptID = resp["id"]
        self.model.setScript(edgeID, scriptID)
