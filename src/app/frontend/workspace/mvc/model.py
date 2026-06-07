from collections import defaultdict, deque

from PyQt5.QtCore import QObject, pyqtSignal


class TreeModel(QObject):
    nodeCreated_ = pyqtSignal(str)
    nodeUpdated_ = pyqtSignal(str)
    modelClear_ = pyqtSignal()
    modelReset_ = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.root = None
        self.parents = {}
        self.children = defaultdict(list)
        self.data = {}

    def createRoot(self, nodeID, data):
        self.root = nodeID
        self.data[nodeID] = data

        self.nodeCreated_.emit(nodeID)

    def createNode(self, nodeID, parentID, data):
        self.children[parentID].append(nodeID)
        self.parents[nodeID] = parentID
        self.data[nodeID] = data

        self.nodeCreated_.emit(nodeID)

    def updateNode(self, nodeID, data):
        self.data[nodeID] = data

        self.nodeUpdated_.emit(nodeID)

    def nodes(self):
        return list(self.data.keys())

    def parent(self, nodeID):
        if self.root == nodeID:
            return None

        return self.parents[nodeID]

    def nodeData(self, nodeID):
        return self.data[nodeID]

    def clear(self):
        self.modelClear_.emit()

        self.root = None
        self.parents.clear()
        self.children.clear()
        self.data.clear()

    def nodeIter(self, node=None, children=None):
        children = children or self.children
        start = self.root if node is None else node

        queue = deque([start])

        while queue:
            parent = queue.popleft()
            yield parent
            for child in children[parent]:
                queue.append(child)

    def serialize(self):
        return {
            "root": self.root,
            "parents": self.parents,
            "children": self.children,
            "data": self.data,
        }

    def deserialize(self, state):
        self.clear()

        rootID = state["root"]
        self.createRoot(
            rootID,
            state["data"][rootID],
        )

        children = defaultdict(list, state["children"])
        parents = state["parents"]

        nodeIter = self.nodeIter(rootID, children)
        for id in nodeIter:
            if id == rootID:
                continue

            data = state["data"][id]
            self.createNode(
                id,
                parents[id],
                data,
            )

        self.modelReset_.emit()
