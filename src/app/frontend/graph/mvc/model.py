from PyQt5.QtCore import QObject, pyqtSignal


class GraphModel(QObject):
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

    def setNodeData(self, nodeID, data):
        self.nodeData[nodeID] = data

    def setEdgeData(self, nid1, nid2, data):
        edgeID = (nid1, nid2)
        self.edgeData[edgeID] = data

    def getNodeData(self, nodeID):
        return self.nodeData[nodeID]

    def getEdgeData(self, nid1, nid2):
        edgeID = (nid1, nid2)
        return self.edgeData[edgeID]

    def clear(self):
        self.nodes.clear()
        self.edges.clear()

        self.nodeData.clear()
        self.edgeData.clear()
