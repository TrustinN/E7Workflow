from src.app.frontend.components import Capability, Component, Serializer

from .controller import GraphController
from .repository import GraphRepository


class GraphSerializerComponent(Component):
    IMPORT = "Import"
    EXPORT = "Export"

    def __init__(
        self,
        serializer: Serializer,
    ):
        super().__init__()
        self.serializer = serializer

        importCapability = Capability(self.IMPORT, self.serializer.restore)
        exportCapability = Capability(self.EXPORT, self.serializer.export)

        self.registerCapability(importCapability)
        self.registerCapability(exportCapability)


class GraphSerializer(Serializer):
    def __init__(
        self,
        controller: GraphController,
        repository: GraphRepository,
    ):
        super().__init__()
        self.controller = controller
        self.repository = repository

    def export(self):
        graphs = self.repository.getGraph()

        for graphID, graphData in graphs.items():
            nodes = graphData.get("nodes")
            edges = graphData.get("edges")
            graphConfig = graphData.get("data")

            for nodeID in nodes:
                nodeData = self.controller.readNode(graphID, nodeID)
                self.repository.updateNode(graphID, nodeID, nodeData)

        self.repository.exportGraph()

    def restore(self):
        self.controller.clearState()
        self.repository.importGraph()

        graphs = self.repository.getGraph()

        for graphID, graphData in graphs.items():
            nodes = graphData.get("nodes")
            edges = graphData.get("edges")
            graphConfig = graphData.get("data")
            self.controller.createGraph(graphID)

            for nodeID, nodeData in nodes.items():
                self.controller.createNode(graphID, nodeID)
                self.controller.updateNode(graphID, nodeID, nodeData)

            for edgeID, edgeData in edges.items():
                id1 = edgeData.get("id1")
                id2 = edgeData.get("id2")
                self.controller.createEdge(graphID, edgeID, id1, id2)
