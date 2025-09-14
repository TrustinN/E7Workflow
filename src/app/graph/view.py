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
        self.edges: dict[any, GraphicsArrowItem] = {}
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

    def createEdge(self, id1, id2):
        key = (id1, id2)

        n1 = self.nodes[id1]
        n2 = self.nodes[id2]
        arrow = GraphicsArrowItem(n1.pos(), n2.pos())
        n1.emitter.onMove_.connect(arrow.setStart)
        n2.emitter.onMove_.connect(arrow.setEnd)

        self.edges[key] = arrow
        self.addItem(arrow)

    def readEdge(self, id1, id2):
        edge = self.edges[(id1, id2)]
        return edge.getData()

    def updateEdge(self, id1, id2, data):
        edge = self.edges[(id1, id2)]
        edge.setData(data)
