import math
from collections import defaultdict

import cv2
import numpy as np
from PyQt5.QtCore import QObject, QThread, pyqtSignal

from src.app.components.action.service import ActionRoute
from src.app.components.runtime.service import RuntimeRoute
from src.app.components.script.service import ScriptRoute
from src.app.components.workspace.model import WorkspaceSchema
from src.app.components.workspace.service import WorkspaceRoute
from src.router.routing import Client, Link


class ExecutionEdge:
    def __init__(
        self,
        edgeID: str,
        priority: int,
        scriptID: str,
        client: Client,
    ):
        self.edgeID = edgeID
        self.priority = priority
        self.scriptID = scriptID
        self.client = client

    def execute(self, context: dict):
        if self.scriptID is None:
            return True  # default always runs the edge

        resp = self.client.post(
            Link(ScriptRoute.NAME, ScriptRoute.SCRIPT, self.scriptID),
            context,
        )
        return resp["result"]


class ExecutionNode:
    def __init__(
        self,
        nodeID: str,
        actionID: str,
        preAction: str,
        postAction: str,
        client: Client,
    ):
        self.nodeID = nodeID
        self.actionID = actionID
        self.preAction = preAction
        self.postAction = postAction
        self.client = client

    def createActionParams(self):
        resp = self.client.get(
            Link(WorkspaceRoute.NAME, WorkspaceRoute.WORKSPACE, self.nodeID)
        )
        schema = WorkspaceSchema.fromData(resp)
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
        return data

    def executeAction(self):
        return self.client.post(
            Link(ActionRoute.NAME, ActionRoute.ACTION, self.actionID),
            self.createActionParams(),
        )

    def executePreAction(self, context: dict):
        if not self.preAction:
            return

        namespace = {
            "__builtins__": __builtins__,
            "math": math,
            "np": np,
            "cv2": cv2,
        }

        exec(self.preAction, namespace)
        namespace["preAction"](context)

    def executePostAction(self, actionResult: dict, context: dict):
        if not self.postAction:
            return

        namespace = {
            "__builtins__": __builtins__,
            "math": math,
            "np": np,
            "cv2": cv2,
        }

        exec(self.postAction, namespace)
        namespace["postAction"](context, actionResult)

    def run(self, context: dict):
        self.executePreAction(context)
        result = self.executeAction()
        self.executePostAction(result, context)
        return result


class ExecutionGraph:
    def __init__(self):
        self.entry: str = None

        self.nodes: dict[str, ExecutionNode] = {}
        self.edges: dict[str, ExecutionEdge] = {}
        self.targets: dict[str, str] = {}

        self.adjacency: dict[str, set] = defaultdict(set)

    def addNode(self, nodeID: str, node: ExecutionNode):
        self.nodes[nodeID] = node

    def addEdge(self, edgeID: str, source: str, target: str, edge: ExecutionEdge):
        self.edges[edgeID] = edge
        self.adjacency[source].add(edgeID)
        self.targets[edgeID] = target

    def getTraversalOrder(self, nodeID: str, context: dict) -> list[ExecutionEdge]:
        edges = self.adjacency[nodeID]
        executionEdges = [self.edges[edgeID] for edgeID in edges]
        executionEdges = sorted(executionEdges, key=lambda edge: edge.priority)
        filteredEdges = []
        for edge in executionEdges:
            if edge.execute(context):
                filteredEdges.append(edge)

        return filteredEdges

    def getTarget(self, edgeID: str) -> ExecutionNode:
        target = self.targets[edgeID]
        return self.nodes[target]

    def setEntry(self, entryID: str):
        self.entry = entryID

    def execute(self, context: dict, maxIterations=10):
        if self.entry is None:
            return

        root = self.nodes[self.entry]
        stack = [root]

        while stack:

            if maxIterations <= 0:
                break

            node = stack.pop()
            node.run(context)

            edges = self.getTraversalOrder(node.nodeID, context)
            for edge in edges[::-1]:
                target = self.getTarget(edge.edgeID)
                stack.append(target)

            maxIterations -= 1


class ExecutionWorker(QObject):
    contextUpdate = pyqtSignal(dict)
    finished = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

    def run(self, graph: ExecutionGraph, context: dict):
        if graph.entry is None:
            return

        root = graph.nodes[graph.entry]
        stack = [root]

        while stack:

            node = stack.pop()
            node.run(context)
            self.contextUpdate.emit(context)

            edges = graph.getTraversalOrder(node.nodeID, context)
            for edge in edges[::-1]:
                target = graph.getTarget(edge.edgeID)
                stack.append(target)

        self.finished.emit()


class ExecutionController(QObject):
    executeGraph = pyqtSignal(object, dict)
    executionFinished = pyqtSignal()

    def __init__(self, client: Client, parent=None):
        super().__init__(parent)
        self.client = client

        self.workerThread = QThread()
        self.worker = ExecutionWorker()
        self.worker.moveToThread(self.workerThread)

        self.workerThread.finished.connect(self.worker.deleteLater)
        self.executeGraph.connect(self.worker.run)
        self.worker.contextUpdate.connect(self.notifyContextUpdate)
        self.worker.finished.connect(self.executionFinished.emit)
        self.workerThread.start()

    def notifyContextUpdate(self, context: dict):
        self.client.put(Link(RuntimeRoute.NAME, RuntimeRoute.ITEM), context)
