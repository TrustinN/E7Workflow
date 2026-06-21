from PyQt5.QtCore import QSignalBlocker, pyqtSignal
from PyQt5.QtWidgets import QGraphicsScene

from src.app.components.graph.model import GraphModel

from .arrow import GraphicsArrowItem
from .node import GraphicsNode


class GraphScene(QGraphicsScene):
    nodeCreated = pyqtSignal(str)
    edgeCreated = pyqtSignal(str)

    nodeUpdated = pyqtSignal(str)
    edgeUpdated = pyqtSignal(str)

    nodeSelected = pyqtSignal(str)
    edgeSelected = pyqtSignal(str)
    selectionCleared = pyqtSignal()

    def __init__(self, model: GraphModel):
        super().__init__()
        self.setSceneRect(0, 0, 400, 300)

        self.model = model
        self.model.nodeCreated.connect(self.createNode)
        self.model.edgeCreated.connect(self.createEdge)

        self.model.nodeUpdated.connect(self.updateNode)

        self.nodeUpdated.connect(self.updateModelNode)
        self.selectionChanged.connect(self.onSelectionChanged)

        self.nodes: dict[str, GraphicsNode] = {}
        self.edges: dict[str, GraphicsArrowItem] = {}

    def updateModelNode(self, id):
        data = self.nodes[id].getData()
        self.model.updateNode(id, data)

    def createNode(self, id):
        node = GraphicsNode()

        schema = self.model.getNode(id)
        node.setData(schema.toData())
        node.emitter.onMove.connect(lambda: self.nodeUpdated.emit(id))

        self.nodes[id] = node
        self.addItem(node)

        self.nodeCreated.emit(id)

    def readNode(self, id) -> dict:
        node = self.nodes[id]
        return node.getData()

    def updateNode(self, id):
        node = self.nodes[id]
        schema = self.model.getNode(id)
        node.setData(schema.toData())

    def createEdge(self, id):
        schema = self.model.getEdge(id)
        id1 = schema.source
        id2 = schema.target

        n1 = self.nodes[id1]
        n2 = self.nodes[id2]
        arrow = GraphicsArrowItem()
        arrow.setPosition(n1.center(), n2.center())
        n1.emitter.onMove.connect(arrow.setStart)
        n2.emitter.onMove.connect(arrow.setEnd)

        self.edges[id] = arrow
        self.addItem(arrow)

        self.edgeCreated.emit(id)

    def setNodeVisible(self, id, show=True):
        with QSignalBlocker(self):
            if show:
                self.nodes[id].show()
            else:
                self.nodes[id].hide()

    def setEdgeVisible(self, id, show=True):
        with QSignalBlocker(self):
            if show:
                self.edges[id].show()
            else:
                self.edges[id].hide()

    def hideAll(self):
        with QSignalBlocker(self):
            for node in self.nodes.values():
                node.hide()

            for edge in self.edges.values():
                edge.hide()

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
            self.selectionCleared.emit()
            return

        node = selected[0]
        for id, graphicsNode in self.nodes.items():
            if graphicsNode is node:
                self.nodeSelected.emit(id)
                break

        for id, graphicsEdge in self.edges.items():
            if graphicsEdge is node:
                self.edgeSelected.emit(id)
                break
