from src.app.components.graph.model import EdgeSchema
from src.app.components.graph.service import GraphRoute
from src.app.components.runner.model import RunnerModel
from src.app.components.runtime.model import RuntimeSchema
from src.app.components.runtime.service import RuntimeRoute
from src.router.routing import Client, Link

from .execution import ExecutionEdge, ExecutionGraph, ExecutionNode


class ExecutionBuilder:
    def __init__(self, model: RunnerModel, client: Client):
        self.model = model
        self.client = client

    def createNode(self, nodeID: str, context: dict) -> ExecutionNode:
        node = self.model.getNode(nodeID)
        if node is None:
            return None

        return ExecutionNode(
            nodeID=nodeID,
            actionID=node.actionID,
            preAction=node.preAction,
            postAction=node.postAction,
            context=context,
            client=self.client,
        )

    def createEdge(self, edgeID: str, context: dict) -> ExecutionEdge:
        runnerEdge = self.model.getEdge(edgeID)

        return ExecutionEdge(
            edgeID=edgeID,
            priority=runnerEdge.priority,
            scriptID=runnerEdge.scriptID,
            context=context,
            client=self.client,
        )

    def getContext(self):
        resp = self.client.get(Link(RuntimeRoute.NAME, RuntimeRoute.ITEM))
        context = {}
        for key, val in resp.items():
            item = RuntimeSchema.fromData(val)
            context[key] = item.value

        return context

    def getNodes(self) -> list[str]:
        resp = self.client.get(Link(GraphRoute.NAME, GraphRoute.NODE))
        return resp["nodes"]

    def getNodeEdges(self, nodeID) -> list[str]:
        resp = self.client.get(
            Link(GraphRoute.NAME, GraphRoute.NODE, nodeID, GraphRoute.EDGE)
        )
        return resp["edges"]

    def getEdge(self, edgeID):
        resp = self.client.get(Link(GraphRoute.NAME, GraphRoute.EDGE, edgeID))
        return EdgeSchema.fromData(resp)

    def createGraph(self):
        context = self.getContext()
        nodeList = self.getNodes()

        graph = ExecutionGraph()
        graph.setEntry(self.model.getEntry())

        for nodeID in nodeList:
            executionNode = self.createNode(nodeID, context)
            if executionNode is None:
                continue

            graph.addNode(nodeID, executionNode)

            for edgeID in self.getNodeEdges(nodeID):
                executionEdge = self.createEdge(edgeID, context)
                edge = self.getEdge(edgeID)

                graph.addEdge(edgeID, edge.source, edge.target, executionEdge)

        return graph
