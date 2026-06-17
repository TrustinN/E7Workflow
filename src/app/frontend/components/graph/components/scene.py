from functools import partial

from PyQt5.QtCore import QSignalBlocker, pyqtSignal
from PyQt5.QtWidgets import QGraphicsScene

from .arrow import EdgeSchema, GraphicsArrowItem
from .node import (
    GraphicsCircleNode,
    GraphicsNode,
    GraphicsRectNode,
    NodeSchema,
    NodeType,
)


class GraphScene(QGraphicsScene):
    nodeMoved_ = pyqtSignal(str)
    edgeMoved_ = pyqtSignal(str)
    nodeSelected_ = pyqtSignal(str)
    nodeDeselected_ = pyqtSignal()
    edgeSelected_ = pyqtSignal(str)
    edgeDeselected_ = pyqtSignal()

    nodeCreated_ = pyqtSignal(str)
    edgeCreated_ = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setSceneRect(0, 0, 400, 300)
        self.nodes: dict[str, GraphicsNode] = {}
        self.edges: dict[str, GraphicsArrowItem] = {}
        self.edgeBindings: dict[str, tuple[str, str]] = {}
        self.selectionChanged.connect(self.onSelectionChanged)

    def selectNode(self, id):
        with QSignalBlocker(self):
            super().clearSelection()
            self.nodes[id].setSelected(True)

    def unselectNode(self, id):
        with QSignalBlocker(self):
            self.nodes[id].setSelected(False)

    def selectEdge(self, id):
        with QSignalBlocker(self):
            super().clearSelection()
            self.edges[id].setSelected(True)

    def unselectEdge(self, id):
        with QSignalBlocker(self):
            self.edges[id].setSelected(False)

    def clearSelection(self):
        with QSignalBlocker(self):
            super().clearSelection()

    def onSelectionChanged(self):
        selected = self.selectedItems()
        if not selected:
            self.nodeDeselected_.emit()
            return

        node = selected[0]
        for id, graphicsNode in self.nodes.items():
            if graphicsNode is node:
                self.nodeSelected_.emit(id)
                break

        for id, graphicsEdge in self.edges.items():
            if graphicsEdge is node:
                self.edgeSelected_.emit(id)
                break

    def createNode(self, id, nodeType=NodeType.RECTANGLE):
        node = None
        if nodeType == NodeType.RECTANGLE:
            node = GraphicsRectNode()

        elif nodeType == NodeType.CIRCLE:
            node = GraphicsCircleNode()

        self.nodes[id] = node

        onNodeMoved = partial(self.nodeMoved_.emit, id)
        node.emitter.onMove_.connect(lambda pos: onNodeMoved())

        self.addItem(node)
        self.nodeCreated_.emit(id)

    def readNode(self, id) -> NodeSchema:
        node = self.nodes[id]
        return node.getData()

    def readEdge(self, id) -> EdgeSchema:
        id1, id2 = self.edgeBindings[id]

        schema = self.edges[id].getData()
        schema.start = id1
        schema.end = id2

        return schema

    def updateNode(self, id, data: NodeSchema):
        node = self.nodes[id]
        node.setData(data)

    def createEdge(self, id, id1, id2):
        n1 = self.nodes[id1]
        n2 = self.nodes[id2]
        arrow = GraphicsArrowItem(n1.center(), n2.center())
        n1.emitter.onMove_.connect(arrow.setStart)
        n2.emitter.onMove_.connect(arrow.setEnd)

        edgeMoved = partial(self.edgeMoved_.emit, id)
        arrow.emitter.onMove_.connect(edgeMoved)

        self.edges[id] = arrow
        self.edgeBindings[id] = (id1, id2)
        self.addItem(arrow)
        self.edgeCreated_.emit(id)
