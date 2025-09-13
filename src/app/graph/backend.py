from nanoid import generate


class GraphBackend:
    def __init__(self):
        self.graphs = {}

    def createGraph(self, userData=None):
        if userData is None:
            userData = {}

        graphID = generate()
        data = {"nodes": {}, "edges": {}, "data": userData}
        self.graphs[graphID] = data
        return graphID, data

    def createNode(self, graphID, userData=None):
        if userData is None:
            userData = {}

        nodes = self.graphs[graphID]["nodes"]
        nodeID = generate()
        data = {"data": userData}
        nodes[nodeID] = data
        return nodeID, data

    def createEdge(self, graphID, id1, id2, userData=None):
        if userData is None:
            userData = {}

        edges = self.graphs[graphID]["edges"]
        data = {"startNodeID": id1, "endNodeID": id2, "data": userData}
        edgeID = generate()
        edges[edgeID] = data
        return edgeID, data

    def updateNode(self, graphID, id, data):
        pass

    def updateEdge(self, graphID, id1, id2, data):
        pass
