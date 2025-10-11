from src.app.frontend.components import Capability, Component, Serializer

from .gui import GraphUI


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
    def __init__(self, graphUI: GraphUI):
        super().__init__()
        self.gui = graphUI
        self.repository = graphUI.repository

    def controller(self, graphID):
        return self.gui.controller(graphID)

    def export(self):
        graphs = self.repository.getGraph()

        for graphID, graphData in graphs.items():
            nodes = graphData.get("nodes")
            edges = graphData.get("edges")
            graphConfig = graphData.get("data")

            controller = self.controller(graphID)
            for nodeID in nodes:
                nodeData = controller.readNode(graphID, nodeID)
                self.repository.updateNode(graphID, nodeID, nodeData)

        self.repository.exportGraph()

    def restore(self):
        self.gui.clear()

        graphs = self.repository.getGraph()

        for graphID, graphData in graphs.items():
            controller, _ = self.gui.createController(graphID)

            nodes = graphData.get("nodes")
            edges = graphData.get("edges")
            graphConfig = graphData.get("data")

            controller.createGraph(graphID)

            for nodeID, nodeData in nodes.items():
                controller.createNode(graphID, nodeID)
                controller.updateNode(graphID, nodeID, nodeData)

            for edgeID, edgeData in edges.items():
                id1 = edgeData.get("id1")
                id2 = edgeData.get("id2")
                controller.createEdge(graphID, edgeID, id1, id2)
