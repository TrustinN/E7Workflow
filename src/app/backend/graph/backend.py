from nanoid import generate


class GraphBackend:
    def __init__(self):
        self.graphs = {}

    def createGraph(self, data):
        data = data or {"nodes": {}, "edges": {}}

        graphID = generate()
        self.graphs[graphID] = data
        return graphID, data

    def updateGraph(self, graphID, data):
        data = data or {}
        self.graphs[graphID].update(data)

    def createNode(self, graphID, data):
        data = data or {}

        nodes = self.graphs[graphID]["nodes"]
        nodeID = generate()
        nodes[nodeID] = data
        return nodeID, data

    def updateNode(self, graphID, nodeID, data):
        data = data or {}
        self.graphs[graphID]["nodes"][nodeID].update(data)

    def createEdge(self, graphID, data):
        data = data or {}

        edges = self.graphs[graphID]["edges"]
        edgeID = generate()
        edges[edgeID] = data
        return edgeID, data

    def updateEdge(self, graphID, edgeID, data):
        data = data or {}
        self.graphs[graphID]["edges"][edgeID].update(data)

    def clear(self):
        self.graphs.clear()

    def overwrite(self, data):
        self.graphs = data
