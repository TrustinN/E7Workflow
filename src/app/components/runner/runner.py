from src.app.components.action.service import ActionRoute
from src.app.components.graph.model import EdgeSchema
from src.app.components.graph.service import GraphRoute
from src.app.components.script.service import ScriptRoute
from src.app.components.workspace.model import WorkspaceSchema
from src.app.components.workspace.service import WorkspaceRoute
from src.router.routing import Client, Link

from .model import RunnerModel


class Runner:
    def __init__(self, model: RunnerModel, client: Client):
        self.model = model
        self.client = client

    def getWorkspaceSchema(self, id: str) -> WorkspaceSchema:
        resp = self.client.get(Link(WorkspaceRoute.NAME, WorkspaceRoute.WORKSPACE, id))
        return WorkspaceSchema.fromData(resp)

    def getEdge(self, id: str) -> EdgeSchema:
        resp = self.client.get(Link(GraphRoute.NAME, GraphRoute.EDGE, id))
        return EdgeSchema.fromData(resp)

    def getEdges(self, id):
        resp = self.client.get(
            Link(GraphRoute.NAME, GraphRoute.NODE, id, GraphRoute.EDGE)
        )
        return resp["edges"]

    def runAction(self, id, data):
        return self.client.post(Link(ActionRoute.NAME, ActionRoute.ACTION, id), data)

    def _evaluateEdge(self, edgeID, context):
        scriptID = self.model.getScript(edgeID)
        if scriptID is None:
            return True  # default always runs the edge

        resp = self.client.post(Link(ScriptRoute.NAME, ScriptRoute.SCRIPT, scriptID))
        return resp["result"]

    def _executeNode(self, nodeID, state):
        action = self.model.getAction(nodeID)
        if action is not None:
            schema = self.getWorkspaceSchema(nodeID)
            geometry = schema.geometry
            data = {
                "systemParams": {
                    "tl": (geometry.x, geometry.y),
                    "br": (
                        geometry.x + geometry.width - 1,
                        geometry.y + geometry.height - 1,
                    ),
                }
            }
            self.runAction(action, data)

        edges = self.getEdges(nodeID)
        for edgeID in edges:
            traverse = self._evaluateEdge(edgeID, state)
            if traverse:
                edge = self.getEdge(edgeID)
                self._executeNode(edge.target, state)

    def execute(self):
        entryID = self.model.getEntry()
        if entryID is None:
            return

        self._executeNode(entryID, {})
