from PyQt5.QtCore import QRectF, Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QGraphicsScene,
    QHBoxLayout,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ..constants import ROOT_ID
from .graph import GraphicsArrowItem, GraphicsNodeItem


class InteractiveGraphScene(QGraphicsScene):
    nodeSelected_ = pyqtSignal(str, str)

    def __init__(self):
        super().__init__()
        self.setSceneRect(0, 0, 400, 300)

        self.nodes: dict[str, GraphicsNodeItem] = {}
        self.edges: dict[tuple[str, str], GraphicsArrowItem] = {}
        self.tuples: dict[str, list[str]] = {}

        self.selectionChanged.connect(self.updateActiveNode)
        self._activeNode = None

    def newSceneNode(self, id: str):
        item = GraphicsNodeItem(QRectF(0, 0, 50, 50), id)
        self.addItem(item)

        self.nodes[id] = item
        self.tuples[id] = []

        self.setActiveNode(item)

        return item

    def newSceneArrow(self, nid1: str, nid2: str):
        n1: GraphicsNodeItem = self.nodes[nid1]
        n2: GraphicsNodeItem = self.nodes[nid2]

        arrow = GraphicsArrowItem(n1.pos(), n2.pos())

        n1.emitter.onMove_.connect(arrow.setStart)
        n2.emitter.onMove_.connect(arrow.setEnd)

        self.addItem(arrow)
        self.edges[(nid1, nid2)] = arrow
        self.tuples[nid1].append(nid2)

    def node(self, id):
        return self.nodes[id]

    def edge(self, nid1, nid2):
        return self.edges[(nid1, nid2)]

    def activeNode(self):
        return self._activeNode

    def setActiveNode(self, node: GraphicsNodeItem):
        if self._activeNode:
            prevId = self._activeNode.id
            self._activeNode = node
            self.nodeSelected_.emit(prevId, node.id)
            return

        self._activeNode = node
        self.nodeSelected_.emit(ROOT_ID, node.id)

    def updateActiveNode(self):
        selected = self.selectedItems()
        if selected:
            item = selected[0]
            self.setActiveNode(item)
        else:
            self._activeNode = None


class GraphEditorActions(QWidget):
    addEdge_ = pyqtSignal()
    addConditionalEdge_ = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()

        self.buttonLabels = [
            "Add Edge",
            "Add Conditional Edge",
        ]
        self.buttons = [QPushButton(label) for label in self.buttonLabels]
        self.signals = [
            self.addEdge_,
            self.addConditionalEdge_,
        ]

        for btn, sig in zip(self.buttons, self.signals):
            self.layout.addWidget(btn)
            btn.clicked.connect(sig.emit)

        self.setLayout(self.layout)


class GraphEditor(QWidget):
    def __init__(self):
        super().__init__()
        self.isListen = False

    def addNode(self, scene: InteractiveGraphScene, id, name=None):
        scene.newSceneNode(id)
        node = scene.node(id)
        if name:
            node.setDisplayText(name)

        return node

    def addEdge(self, scene: InteractiveGraphScene):
        if self.isListen:
            return

        self.isListen = True
        nodeIDs = []

        def defineEdgeEnd():
            activeNode = scene.activeNode()
            if activeNode is None:
                nodeIDs.pop()
                scene.selectionChanged.disconnect(defineEdgeEnd)
                scene.selectionChanged.connect(defineEdgeStart)
                return

            nodeIDs.append(activeNode.id)
            scene.selectionChanged.disconnect(defineEdgeEnd)
            scene.newSceneArrow(*nodeIDs)

            self.isListen = False

        def defineEdgeStart():
            activeNode = scene.activeNode()
            if activeNode:
                nodeIDs.append(activeNode.id)
                scene.selectionChanged.disconnect(defineEdgeStart)
                scene.selectionChanged.connect(defineEdgeEnd)

        activeNode = scene.activeNode()
        if activeNode and activeNode.isSelected():
            nodeIDs.append(activeNode.id)
            scene.selectionChanged.connect(defineEdgeEnd)
        else:
            scene.selectionChanged.connect(defineEdgeStart)

    def reset(self):
        self.isListen = False
