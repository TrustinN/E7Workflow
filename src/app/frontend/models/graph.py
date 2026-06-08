from collections import defaultdict

from PyQt5.QtCore import pyqtSignal

from .model import Model


class GraphModel(Model):
    nodeCreated_ = pyqtSignal(str)
    edgeCreated_ = pyqtSignal(str, str)

    def __init__(self):
        super().__init__()
        # Contains graphID -> node list + edge list
        self.nodes = []
        self.edges = []

        # Contains nodeID -> node data
        self.nodeData = {}

        # Contains edgeID -> edge data
        self.edgeData = {}

    def createNode(self, nodeID, data):
        self.nodes.append(nodeID)
        self.nodeData[nodeID] = data
        self.nodeCreated_.emit(nodeID)

    def createEdge(self, nid1, nid2, data):
        edgeID = (nid1, nid2)
        self.edges.append(edgeID)
        self.edgeData[edgeID] = data
        self.edgeCreated_.emit(nid1, nid2)

    def updateNode(self, nodeID, data):
        self.nodeData[nodeID] = data

    def updateEdge(self, nid1, nid2, data):
        edgeID = (nid1, nid2)
        self.edgeData[edgeID] = data

    def getNodeData(self, nodeID):
        return dict(self.nodeData[nodeID])

    def getEdgeData(self, nid1, nid2):
        edgeID = (nid1, nid2)
        return dict(self.edgeData[edgeID])

    def nodeIter(self):
        for nodeID in self.nodes:
            yield nodeID

    def edgeIter(self):
        for edgeID in self.edges:
            yield edgeID

    def clear(self):
        self.modelClear_.emit()

        self.nodes.clear()
        self.edges.clear()

        self.nodeData.clear()
        self.edgeData.clear()

    def serialize(self):
        # Reformat so keys are not tuples
        edgeData = defaultdict(dict[str, object])

        for e1, e2 in self.edgeData:
            edgeData[e1][e2] = self.getEdgeData(e1, e2)

        edges = []
        for e1, e2 in self.edges:
            edges.append([e1, e2])

        return {
            "nodes": self.nodes,
            "edges": self.edges,
            "nodeData": self.nodeData,
            "edgeData": edgeData,
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

        for e1, e2 in edges:
            data = edgeData[e1][e2]
            self.createEdge(e1, e2, data)

        self.modelReset_.emit()
