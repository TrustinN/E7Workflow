import json

from src.app.components.action.service import ActionRoute
from src.app.components.script.service import ScriptRoute
from src.app.components.workspace.model import WorkspaceSchema
from src.app.components.workspace.service import WorkspaceRoute
from src.router.routing import Client, Link

from .model import RunnerEdgeSchema, RunnerModel, RunnerNodeSchema


class RunnerManager:
    def __init__(self, model: RunnerModel, client: Client):
        self.client = client
        self.model = model

    def isActionAssignable(self, nodeID: str) -> bool:
        link = Link(WorkspaceRoute.NAME, WorkspaceRoute.WORKSPACE, nodeID)
        resp = self.client.get(link)
        wks = WorkspaceSchema.fromData(resp)
        return len(wks.children) == 0

    def createNode(self, nodeID: str) -> str:
        self.model.setNode(nodeID, RunnerNodeSchema())

    def setAction(self, nodeID: str) -> str:
        if not self.isActionAssignable(nodeID):
            return None

        link = Link(ActionRoute.NAME, ActionRoute.CREATE)
        resp = self.client.post(link)
        actionID = resp["id"]

        self.model.updateNode(nodeID, {"actionID": actionID})
        return actionID

    def unsetAction(self, nodeID: str):
        node = self.model.getNode(nodeID)
        if not node.actionID:
            return

        link = Link(ActionRoute.NAME, ActionRoute.ACTION, node.actionID)
        self.client.delete(link)
        node.actionID = None

    def createScript(self, edgeID: str) -> str:
        self.model.setEdge(edgeID, RunnerEdgeSchema())

    def setScript(self, edgeID: str) -> str:
        link = Link(ScriptRoute.NAME, ScriptRoute.SCRIPT)
        resp = self.client.get(link)
        scriptID = resp["id"]

        self.model.updateEdge(edgeID, {"scriptID": scriptID})
        return scriptID

    def unsetScript(self, edgeID: str):
        edge = self.model.getEdge(edgeID)
        edge.scriptID = None

    def setEntry(self, nodeID: str) -> str:
        prev = self.model.getEntry()
        self.model.setEntry(nodeID)
        return prev

    def unsetEntry(self):
        prev = self.model.getEntry()
        self.model.setEntry(None)
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
