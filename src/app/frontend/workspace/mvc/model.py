from PyQt5.QtCore import QObject, pyqtSignal


class TreeModel(QObject):
    nodeCreated_ = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.root = None
        self.parents = {}
        self.data = {}

    def createNode(self, nodeID, parentID, data):
        self.parents[nodeID] = parentID

        if self.root is None:
            self.root = nodeID
            self.parents[nodeID] = nodeID

        self.data[nodeID] = data
        self.nodeCreated_.emit(nodeID)

    def parentNode(self, nodeID):
        if self.root == nodeID:
            return None

        return self.parents[nodeID]

    def nodeData(self, nodeID):
        return self.data[nodeID]

    def clear(self):
        self.parents.clear()
        self.data.clear()
