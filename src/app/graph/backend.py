from nanoid import generate


class GraphBackend:
    def __init__(self):
        self.graphs = {}
        self.context = {}

    def setContext(self, data):
        self.context = data

    def createGraph(self, userData=None):
        userData = userData or {}

        graphID = generate()
        data = {"nodes": {}, "edges": {}, "data": userData}
        self.graphs[graphID] = data
        return graphID, data

    def updateGraph(self, graphID, data):
        self.graphs[graphID]["data"].update(data)

    def createNode(self, graphID, userData=None):
        userData = userData or {}

        nodes = self.graphs[graphID]["nodes"]
        nodeID = generate()
        nodes[nodeID] = userData
        return nodeID, userData

    def updateNode(self, graphID, nodeID, data):
        self.graphs[graphID]["nodes"][nodeID].update(data)

    def createEdge(self, graphID, userData=None):
        userData = userData or {}

        edges = self.graphs[graphID]["edges"]
        edgeID = generate()
        edges[edgeID] = userData
        return edgeID, userData

    def updateEdge(self, graphID, edgeID, data):
        self.graphs[graphID]["edges"][edgeID].update(data)

    def clear(self):
        self.graphs.clear()
        self.context.clear()

    def overwrite(self, data):
        self.graphs = data
