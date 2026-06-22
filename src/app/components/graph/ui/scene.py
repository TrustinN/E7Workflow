from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QGraphicsScene

from .arrow import GraphicsArrowItem
from .node import GraphicsNode


class GraphScene(QGraphicsScene):
    nodeCreated = pyqtSignal(str)
    edgeCreated = pyqtSignal(str)

    nodeUpdated = pyqtSignal(str)
    edgeUpdated = pyqtSignal(str)

    nodeSelected = pyqtSignal(str)
    edgeSelected = pyqtSignal(str)
    rootSelected = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setSceneRect(0, 0, 400, 300)

        self.nodes: dict[str, GraphicsNode] = {}
        self.edges: dict[str, GraphicsArrowItem] = {}

    def createNode(self, id):
        node = GraphicsNode()
        node.emitter.onMove.connect(lambda: self.nodeUpdated.emit(id))
        node.emitter.onMousePress.connect(lambda: self.nodeSelected.emit(id))

        self.nodes[id] = node
        self.addItem(node)

        self.nodeCreated.emit(id)

    def readNode(self, id) -> dict:
        node = self.nodes[id]
        return node.getData()

    def updateNode(self, id, data):
        node = self.nodes[id]
        node.setData(data)

    def createEdge(self, id, source, target):
        n1 = self.nodes[source]
        n2 = self.nodes[target]
        arrow = GraphicsArrowItem()
        arrow.setPosition(n1.center(), n2.center())
        n1.emitter.onMove.connect(lambda: arrow.setStart(n1.center()))
        n2.emitter.onMove.connect(lambda: arrow.setEnd(n2.center()))

        arrow.emitter.onMousePress.connect(lambda: self.edgeSelected.emit(id))

        self.edges[id] = arrow
        self.addItem(arrow)

        self.edgeCreated.emit(id)

    def readEdge(self, id) -> dict:
        edge = self.edges[id]
        return edge.getData()

    def updateEdge(self, id, data):
        edge = self.edges[id]
        edge.setData(data)

    def setNodeVisible(self, id, show=True):
        if show:
            self.nodes[id].show()
            self.nodeUpdated.emit(id)
        else:
            self.nodes[id].hide()
            self.nodeUpdated.emit(id)

    def setEdgeVisible(self, id, show=True):
        if show:
            self.edges[id].show()
            self.edgeUpdated.emit(id)
        else:
            self.edges[id].hide()
            self.edgeUpdated.emit(id)

    def hideAll(self):
        for id, node in self.nodes.items():
            node.hide()
            self.nodeUpdated.emit(id)

        for id, edge in self.edges.items():
            edge.hide()
            self.edgeUpdated.emit(id)

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        if not self.selectedItems():
            self.rootSelected.emit()

    def selectNode(self, id):
        self.nodes[id].setSelected(True)

    def selectEdge(self, id):
        self.edges[id].setSelected(True)
