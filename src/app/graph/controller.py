from .view import GraphView


class GraphController:
    def __init__(self):
        self.nodeStart = None
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

    def createEdge(self, graphID):
        view = self.scene(graphID)
        id1 = self.nodeStart
        id2 = view.selectedNode()
        if not id2:
            return None

        if not id1:
            self.nodeStart = id2
            return None

        self.nodeStart = None
        view.createEdge(id1, id2)
        return (id1, id2)

    def updateNode(self, graphID, nodeID, data):
        view = self.scene(graphID)
        view.updateNode(nodeID, data)
