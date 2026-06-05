import json

from .mv import GraphMV


class GraphSerializer:
    def __init__(self, graphmv: GraphMV):
        super().__init__()
        self.graphmv = graphmv
        self.path = "graphConfig"

    def controller(self, graphID):
        return self.graphmv.controller(graphID)

    def export(self):
        graphIDs = self.graphmv.controllerIDs()
        config = {}

        for graphID in graphIDs:
            controller = self.controller(graphID)
            graphData = controller.readScene()

            nodes = graphData["nodes"]
            for nodeID in nodes:
                nodeData = self.graphmv.nodeData(nodeID)
                nodes[nodeID]["data"] = nodeData

            graphData["data"] = self.graphmv.graphData(graphID)
            config[graphID] = graphData

        with open(self.path, "w") as f:
            json.dump(config, f, indent=4)

    def restore(self):
        self.graphmv.clear()

        with open(self.path, "r") as f:
            graphs = json.load(f)

            for graphID, graphData in graphs.items():
                self.graphmv.createController(graphID)
                controller = self.graphmv.controller(graphID)

                nodes = graphData.get("nodes")
                edges = graphData.get("edges")
                data = graphData.get("data")
                self.graphmv.setGraphData(graphID, data)

                for nodeID, nodeData in nodes.items():
                    controller.createNode(nodeID)
                    controller.updateNode(nodeID, nodeData)
                    nodeDataID = nodeData["data"]
                    self.graphmv.setNodeData(nodeID, nodeDataID)

                for edgeID, edgeData in edges.items():
                    id1 = edgeData.get("id1")
                    id2 = edgeData.get("id2")
                    controller.createEdge(edgeID, id1, id2)
