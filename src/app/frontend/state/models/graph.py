from collections import defaultdict

from PyQt5.QtCore import pyqtSignal

from .model import Model


class GraphModel(Model):
    nodeCreated_ = pyqtSignal(str)
    edgeCreated_ = pyqtSignal(str)

    nodeUpdated_ = pyqtSignal(str)
    edgeUpdated_ = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.adjacency: dict[str, set] = defaultdict(set)
        self.edges = {}

        # Contains nodeID -> node data
        self.nodeData = {}

        # Contains edgeID -> edge data
        self.edgeData = {}

    def _createNode(self, nodeID, data):
        self.nodeData[nodeID] = data

    def createNode(self, nodeID, data):
        self._createNode(nodeID, data)
        self.nodeCreated_.emit(nodeID)

    def _createEdge(self, edgeID, nid1, nid2, data):
        self.edges[edgeID] = [nid1, nid2]
        self.adjacency[nid1].add(edgeID)
        self.edgeData[edgeID] = data

    def createEdge(self, edgeID, nid1, nid2, data):
        self._createEdge(edgeID, nid1, nid2, data)
        self.edgeCreated_.emit(edgeID)

    def _updateNode(self, nodeID, data):
        self.nodeData[nodeID] = data

    def updateNode(self, nodeID, data):
        self._updateNode(nodeID, data)
        self.nodeUpdated_.emit(nodeID)

    def _updateEdge(self, edgeID, data):
        self.edgeData[edgeID] = data

    def updateEdge(self, edgeID, data):
        self._updateEdge(edgeID, data)
        self.edgeUpdated_.emit(edgeID)

    def getNodeData(self, nodeID):
        return self.nodeData[nodeID].copy()

    def getEdgeData(self, edgeID):
        return self.edgeData[edgeID].copy()

    def getEdges(self, nodeID):
        return self.adjacency[nodeID].copy()

    def getEdge(self, edgeID):
        return self.edges[edgeID]

    def nodeIter(self):
        for nodeID in self.nodeData:
            yield nodeID

    def edgeIter(self):
        for edgeID in self.edgeData:
            yield edgeID

    def clear(self):
        self.adjacency.clear()
        self.edges.clear()

        self.nodeData.clear()
        self.edgeData.clear()

        self.modelClear_.emit()

    def serialize(self):

        return {
            "edges": self.edges,
            "nodeData": self.nodeData,
            "edgeData": self.edgeData,
        }

    def deserialize(self, state):
        edges = state["edges"]
        nodeData = state["nodeData"]
        edgeData = state["edgeData"]

        for nodeID in nodeData:
            data = nodeData[nodeID]
            self._createNode(nodeID, data)

        for edgeID in edges:
            start, end = edges[edgeID]
            data = edgeData[edgeID]
            self._createEdge(edgeID, start, end, data)

        self.modelLoaded_.emit()
