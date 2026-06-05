from .view import GraphView


class GraphController:
    def __init__(self, scene: GraphView):
        self.scene = scene

    def createNode(self, nodeID):
        self.scene.createNode(nodeID)

    def readNode(self, nodeID):
        return self.scene.readNode(nodeID)

    def createEdge(self, edgeID, id1, id2):
        self.scene.createEdge(edgeID, id1, id2)

    def updateNode(self, nodeID, data):
        self.scene.updateNode(nodeID, data)

    def readScene(self):
        return self.scene.getData()

    def clearState(self):
        self.scene.deleteLater()
        self.scene = None
