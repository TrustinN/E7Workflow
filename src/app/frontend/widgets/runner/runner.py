from src.app.backend.action import ActionRoute
from src.app.frontend.state import Context, Document
from src.router.routing import Client, Link


class Runner:
    def __init__(self, context: Context, document: Document, client: Client):
        self.context = context
        self.document = document
        self.client = client

    def _executeNode(self, nodeID):
        if self.context.workspaceModel.isLeaf(nodeID):
            if not self.context.actionModel.hasKey(nodeID):
                return  # no action binding

            actionData = self.context.actionModel.getData(nodeID)
            geometry = self.document.workspace.nodes[nodeID].geometry
            actionData["systemParams"] = {
                "tl": (geometry.x, geometry.y),
                "br": (
                    geometry.x + geometry.width - 1,
                    geometry.y + geometry.height - 1,
                ),
            }

            link = Link(ActionRoute.NAME, ActionRoute.ACTION, actionData["name"])
            self.client.post(
                link,
                actionData,
            )

        edges = self.context.graphModel.getEdges(nodeID)
        for edgeID in edges:
            _, e2 = self.context.graphModel.getEdge(edgeID)
            self._executeNode(e2)

    def execute(self, data):
        entryID = self.context.runnerModel.getSelected()
        if entryID is None:
            return

        self._executeNode(entryID)
