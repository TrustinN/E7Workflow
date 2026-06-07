import json

from PyQt5.QtCore import QObject, pyqtSignal


class GraphModel(QObject):
    nodeCreated_ = pyqtSignal(str)
    edgeCreated_ = pyqtSignal(str, str)
    modelClear_ = pyqtSignal()
    modelReset_ = pyqtSignal()

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
        return self.nodeData[nodeID]

    def getEdgeData(self, nid1, nid2):
        edgeID = (nid1, nid2)
        return self.edgeData[edgeID]

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

        for edgeID in edges:
            data = edgeData[edgeID]
            self.createEdge(edgeID[0], edgeID[1], data)

        self.modelReset_.emit()


class GraphModelSerializer:
    def __init__(self):
        pass

    def export(self, model: GraphModel, path: str):
        state = model.serialize()
        with open(path, "w") as f:
            json.dump(state, f, indent=4)

    def restore(self, path: str):
        with open(path, "r") as f:
            return json.load(f)
