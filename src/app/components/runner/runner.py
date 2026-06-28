from src.app.components.action.model import ActionSchema
from src.app.components.action.service import ActionRoute
from src.app.components.graph.model import EdgeSchema
from src.app.components.graph.service import GraphRoute
from src.app.components.runtime.model import RuntimeSchema, RuntimeType
from src.app.components.runtime.service import RuntimeRoute
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

    def getContext(self):
        resp = self.client.get(Link(RuntimeRoute.NAME, RuntimeRoute.ITEM))
        context = {}
        for key, val in resp.items():
            item = RuntimeSchema.fromData(val)
            context[key] = item.value
        return context

    def runAction(self, actionID, data):
        return self.client.post(
            Link(ActionRoute.NAME, ActionRoute.ACTION, actionID), data
        )

    def updateContext(self, actionID, result, context):
        data = self.client.get(Link(ActionRoute.NAME, ActionRoute.ACTION, actionID))
        action = ActionSchema.fromData(data)

        userParams = action.userParams
        if "dest" not in userParams:
            return

        dest = userParams["dest"]["value"]
        link = Link(RuntimeRoute.NAME, RuntimeRoute.ITEM, dest)
        payload = {"name": dest, "type": RuntimeType.IMAGE.name, "value": result}
        if dest not in context:
            self.client.post(link, payload)
        else:
            self.client.put(link, payload)

    def _evaluateEdge(self, edgeID, context):
        scriptID = self.model.getScript(edgeID)
        if scriptID is None:
            return True  # default always runs the edge

        resp = self.client.post(
            Link(ScriptRoute.NAME, ScriptRoute.SCRIPT, scriptID),
            context,
        )
        return resp["result"]

    def _executeNode(self, nodeID, context):
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
            result = self.runAction(action, data)
            self.updateContext(action, result, context)
            context = self.getContext()

        edges = self.getEdges(nodeID)
        for edgeID in edges:
            traverse = self._evaluateEdge(edgeID, context)
            if traverse:
                edge = self.getEdge(edgeID)
                self._executeNode(edge.target, context)

    def execute(self):
        entryID = self.model.getEntry()
        if entryID is None:
            return

        context = self.getContext()
        self._executeNode(entryID, context)
