from .view import GraphView


class GraphController:
    def __init__(self):
        self.id1 = None
        self.id2 = None
        self.scenes = {}

    def scene(self, id):
        return self.scenes[id]

    def createGraph(self, id):
        view = GraphView()
        self.scenes[id] = view

        return view

    def createNode(self, graphID, nodeID):
        view = self.scene(graphID)
        view.createNode(nodeID)

    def readNode(self, graphID, nodeID):
        view = self.scene(graphID)
        return view.readNode(nodeID)

    def setE1(self, graphID):
        view = self.scene(graphID)
        self.id1 = view.selectedNode()

    def setE2(self, graphID):
        view = self.scene(graphID)
        self.id2 = view.selectedNode()

    def canCreateEdge(self):
        return self.id1 and self.id2

    def createEdge(self, graphID, edgeID, id1=None, id2=None):
        id1, id2 = id1 or self.id1, id2 or self.id2
        view = self.scene(graphID)
        view.createEdge(edgeID, id1, id2)

        self.id1, self.id2 = None, None

        return (id1, id2)

    def updateNode(self, graphID, nodeID, data):
        view = self.scene(graphID)
        view.updateNode(nodeID, data)

    def clearState(self):
        for scene in self.scenes.values():
            scene.deleteLater()

        self.scenes.clear()

        self.id1, self.id2 = None, None
