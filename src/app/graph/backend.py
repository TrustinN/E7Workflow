from nanoid import generate


class GraphBackend:
    def __init__(self):
        self.graphs = {}

    def createGraph(self, userData=None):
        userData = userData or {}

        graphID = generate()
        data = {"nodes": {}, "edges": {}, "data": userData}
        self.graphs[graphID] = data
        return graphID, data

    def createNode(self, graphID, userData=None):
        userData = userData or {}

        nodes = self.graphs[graphID]["nodes"]
        nodeID = generate()
        nodes[nodeID] = userData
        return nodeID, userData

    def createEdge(self, graphID, id1, id2, userData=None):
        userData = userData or {}

        edges = self.graphs[graphID]["edges"]
        data = {"startNodeID": id1, "endNodeID": id2}
        data.update(userData)
        edgeID = generate()
        edges[edgeID] = data
        return edgeID, data

    def updateGraph(self, graphID, data):
        self.graphs[graphID]["data"].update(data)

    def updateNode(self, graphID, nodeID, data):
        self.graphs[graphID]["nodes"][nodeID].update(data)

    def updateEdge(self, graphID, edgeID, data):
        self.graphs[graphID]["edges"][edgeID].update(data)

    def clear(self):
        self.graphs.clear()

    def overwrite(self, data):
        self.graphs = data
