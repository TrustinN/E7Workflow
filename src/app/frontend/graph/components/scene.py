from functools import partial

from PyQt5.QtCore import QPointF, QSignalBlocker, pyqtSignal
from PyQt5.QtWidgets import QGraphicsScene

from .graph import GraphicsArrowItem, GraphicsNodeItem


class GraphScene(QGraphicsScene):
    nodeMoved_ = pyqtSignal(str, QPointF)
    nodePressed_ = pyqtSignal(str)
    nodeSelected_ = pyqtSignal(str)
    nodeDeselected_ = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setSceneRect(0, 0, 400, 300)
        self.nodes: dict[str, GraphicsNodeItem] = {}
        self.edges: dict[str, GraphicsArrowItem] = {}
        self.edgeIds: dict[tuple[str, str], str] = {}
        self.state = {"nodeSelected": None}
        self.selectionChanged.connect(self.onSelectionChanged)

    def selectedNode(self):
        return self.state["nodeSelected"]

    def selectNode(self, id):
        with QSignalBlocker(self):
            super().clearSelection()
            self.nodes[id].setSelected(True)

    def clearSelection(self):
        with QSignalBlocker(self):
            super().clearSelection()

    def onSelectionChanged(self):
        selected = self.selectedItems()
        if not selected:
            self.state["nodeSelected"] = None
            self.nodeDeselected_.emit()
            return

        node = selected[0]
        for id, graphicsNode in self.nodes.items():
            if graphicsNode is node:
                self.state["nodeSelected"] = id
                self.nodeSelected_.emit(id)
                break

    def createNode(self, id):
        node = GraphicsNodeItem()
        self.nodes[id] = node

        onNodeMoved = partial(self.nodeMoved_.emit, id)
        # onNodePressed = partial(self.onNodePressed, id)

        node.emitter.onMove_.connect(onNodeMoved)
        # node.emitter.onMousePress_.connect(onNodePressed)

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
        self.edgeIds[(id1, id2)] = id
        self.addItem(arrow)

    def readEdge(self, id1, id2):
        edgeID = self.edgeIds[(id1, id2)]
        edge = self.edges[edgeID]
        return edge.getData()

    def updateEdge(self, id1, id2, data):
        edgeID = self.edgeIds[(id1, id2)]
        edge = self.edges[edgeID]
        edge.setData(data)

    def getData(self):
        nodeData = {}
        edgeData = {}
        for id in self.nodes:
            nodeData[id] = self.readNode(id)

        for nid1, nid2 in self.edgeIds:
            data = self.readEdge(nid1, nid2)
            data["id1"] = nid1
            data["id2"] = nid2
            edgeData[id] = data

        return {
            "nodes": nodeData,
            "edges": edgeData,
        }
