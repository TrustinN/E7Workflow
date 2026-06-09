from collections import defaultdict

from .model import Model


class GraphModel(Model):
    def __init__(self):
        super().__init__()
        # Contains graphID -> node list + edge list
        self.nodes = []
        self.edges = defaultdict(list)

        # Contains nodeID -> node data
        self.nodeData = {}

        # Contains edgeID -> edge data
        self.edgeData = defaultdict(dict)

    def createNode(self, nodeID, data):
        self.nodes.append(nodeID)
        self.nodeData[nodeID] = data

    def createEdge(self, nid1, nid2, data):
        self.edges[nid1].append(nid2)
        self.edgeData[nid1][nid2] = data

    def updateNode(self, nodeID, data):
        self.nodeData[nodeID] = data

    def updateEdge(self, nid1, nid2, data):
        self.edgeData[nid1][nid2] = data

    def getNodeData(self, nodeID):
        return dict(self.nodeData[nodeID])

    def getEdgeData(self, nid1, nid2):
        return dict(self.edgeData[nid1][nid2])

    def getEdges(self, nodeID):
        return self.edges[nodeID]

    def nodeIter(self):
        for nodeID in self.nodes:
            yield nodeID

    def edgeIter(self):
        for e1 in self.edges:
            for e2 in self.edges[e1]:
                yield (e1, e2)

    def clear(self):
        self.nodes.clear()
        self.edges.clear()

        self.nodeData.clear()
        self.edgeData.clear()

    def serialize(self):

        return {
            "nodes": self.nodes,
            "edges": self.edges,
            "nodeData": self.nodeData,
            "edgeData": self.edgeData,
        }

    def deserialize(self, state):
        self.clear()

        nodes = state["nodes"]
        edges = state["edges"]
        nodeData = state["nodeData"]
        edgeData = state["edgeData"]

        for nodeID in nodes:
            data = nodeData[nodeID]
            self.createNode(nodeID, data)

        for e1 in edges:
            for e2 in edges[e1]:
                data = edgeData[e1][e2]
                self.createEdge(e1, e2, data)
