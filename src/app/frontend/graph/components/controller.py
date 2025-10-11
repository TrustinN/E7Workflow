from .view import GraphView


class GraphController:
    def __init__(self, scene: GraphView):
        self.id1 = None
        self.id2 = None
        self.scene = scene

    def createNode(self, nodeID):
        self.scene.createNode(nodeID)

    def readNode(self, nodeID):
        return self.scene.readNode(nodeID)

    def setE1(self):
        self.id1 = self.scene.selectedNode()

    def setE2(self):
        self.id2 = self.scene.selectedNode()

    def canCreateEdge(self):
        return self.id1 and self.id2

    def createEdge(self, edgeID, id1=None, id2=None):
        id1, id2 = id1 or self.id1, id2 or self.id2
        self.scene.createEdge(edgeID, id1, id2)

        self.id1, self.id2 = None, None

        return (id1, id2)

    def updateNode(self, nodeID, data):
        self.scene.updateNode(nodeID, data)

    def clearState(self):
        self.scene.deleteLater()
        self.id1, self.id2 = None, None
        self.scene = None
