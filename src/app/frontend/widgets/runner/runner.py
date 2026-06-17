import math

import cv2
import numpy as np

from src.app.backend.action import ActionRoute
from src.app.frontend.state import Context, Document
from src.router.routing import Client, Link


class Runner:
    def __init__(self, context: Context, document: Document, client: Client):
        self.context = context
        self.document = document
        self.client = client

    def _evaluateEdge(self, edgeID, context):
        if edgeID not in list(self.context.conditionalModel.keys()):
            return True  # default always runs the edge

        scriptID = self.context.conditionalModel.getData(edgeID)
        data = self.context.codeModel.getData(scriptID)
        code = data["code"]
        namespace = {
            "__builtins__": __builtins__,
            "math": math,
            "np": np,
            "cv2": cv2,
        }

        exec(code, namespace)
        result = namespace["condition"](context)
        return result

    def _executeNode(self, nodeID, state):
        if self.context.workspaceModel.isLeaf(nodeID):
            if self.context.actionModel.hasKey(nodeID):
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
            traverse = self._evaluateEdge(edgeID, state)
            if traverse:
                _, e2 = self.context.graphModel.getEdge(edgeID)
                self._executeNode(e2, state)

    def execute(self, data):
        entryID = self.context.runnerModel.getSelected()
        if entryID is None:
            return

        self._executeNode(entryID, {})
