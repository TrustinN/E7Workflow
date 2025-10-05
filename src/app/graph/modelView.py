from functools import partial

from PyQt5.QtCore import QPointF, pyqtSignal
from PyQt5.QtWidgets import QGraphicsScene

from .graph import GraphicsArrowItem, GraphicsNodeItem


class GraphView(QGraphicsScene):
    nodeMoved_ = pyqtSignal(str, QPointF)
    nodePressed_ = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setSceneRect(0, 0, 400, 300)
        self.nodes: dict[str, GraphicsNodeItem] = {}
        self.edges: dict[str, GraphicsArrowItem] = {}
        self.state = {"nodeSelected": None}

    def selectedNode(self):
        return self.state["nodeSelected"]

    def onNodePressed(self, id):
        self.state["nodeSelected"] = id
        self.nodePressed_.emit(id)

    def createNode(self, id):
        node = GraphicsNodeItem()
        self.nodes[id] = node

        onNodeMoved = partial(self.nodeMoved_.emit, id)
        onNodePressed = partial(self.onNodePressed, id)

        node.emitter.onMove_.connect(onNodeMoved)
        node.emitter.onMousePress_.connect(onNodePressed)

        self.addItem(node)

    def readNode(self, id):
        node = self.nodes[id]
        return node.getData()

    def updateNode(self, id, data):
        node = self.nodes[id]
        node.setData(data)

    def createEdge(self, id, id1, id2):
        n1 = self.nodes[id1]
        n2 = self.nodes[id2]
        arrow = GraphicsArrowItem(n1.pos(), n2.pos())
        n1.emitter.onMove_.connect(arrow.setStart)
        n2.emitter.onMove_.connect(arrow.setEnd)

        self.edges[id] = arrow
        self.addItem(arrow)

    def readEdge(self, id1, id2):
        edge = self.edges[(id1, id2)]
        return edge.getData()

    def updateEdge(self, id1, id2, data):
        edge = self.edges[(id1, id2)]
        edge.setData(data)


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
