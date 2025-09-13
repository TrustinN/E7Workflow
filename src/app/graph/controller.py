from .view import GraphView


class GraphController:
    def __init__(self, state: any, view: GraphView):
        self.graphState = state
        self.view = view

        self.view.nodePressed_.connect(self.onNodePressed)

    def createNode(self, id, data=None):
        self.view.createNode(id)
        if data:
            self.view.updateNode(id, data)

    def readNode(self, id):
        return self.view.readNode(id)

    def updateNode(self, id, data):
        self.view.updateNode(id, data)

    def createEdge(self, id1, id2, data=None):
        self.view.createEdge(id1, id2)
        if data:
            self.view.updateEdge(id1, id2, data)

    def readEdge(self, id1, id2):
        return self.view.readEdge(id1, id2)

    def updateEdge(self, id1, id2, data):
        self.view.updateEdge(id1, id2, data)

    def onNodePressed(self, id):
        self.graphState["selectedNode"] = id

    def selectedNode(self):
        return self.graphState["selectedNode"]
