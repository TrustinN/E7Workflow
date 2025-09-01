from PyQt5.QtCore import QRectF, pyqtSignal
from PyQt5.QtWidgets import QGraphicsScene, QPushButton, QVBoxLayout, QWidget

from .graph import GraphicsArrowItem, GraphicsNodeItem, NodeState, WorkspaceNodeItem


class InteractiveGraphScene(QGraphicsScene):
    nodeSelected_ = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setSceneRect(0, 0, 400, 300)

        self.nodes: dict[str, GraphicsNodeItem] = {}
        self.edges: dict[tuple[str, str], GraphicsArrowItem] = {}
        self.tuples: dict[str, list[str]] = {}

        self.selectionChanged.connect(self.updateActiveNode)
        self._activeNode = None

    def newSceneNode(self, id: str):
        item = WorkspaceNodeItem(QRectF(0, 0, 50, 50), id)
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
        if node == self.activeNode():
            return

        if self._activeNode:
            prevId = self._activeNode.id
            self.node(prevId).setSelected(False)
            self._activeNode = node
            self.nodeSelected_.emit(prevId)
            return

        self._activeNode = node
        self.nodeSelected_.emit(None)

    def updateActiveNode(self):
        selected = self.selectedItems()
        if selected:
            item = selected[0]
            self.setActiveNode(item)
        else:
            self.setActiveNode(None)


class GraphEditorActions(QWidget):
    addEdge_ = pyqtSignal()
    addCrossEdge_ = pyqtSignal()
    addConditionalEdge_ = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()

        self.buttonLabels = [
            "Add Edge",
            "Add Cross Edge",
            "Add Conditional Edge",
        ]
        self.buttons = [QPushButton(label) for label in self.buttonLabels]
        self.signals = [
            self.addEdge_,
            self.addCrossEdge_,
            self.addConditionalEdge_,
        ]

        for btn, sig in zip(self.buttons, self.signals):
            self.layout.addWidget(btn)
            btn.clicked.connect(sig.emit)

        self.setLayout(self.layout)


class GraphEditor(QWidget):
    edgeCreated_ = pyqtSignal(object)
    crossEdgeCreated_ = pyqtSignal(object)

    def __init__(self):
        super().__init__()

    def addNode(self, scene: InteractiveGraphScene, id, name=None):
        scene.newSceneNode(id)
        node = scene.node(id)
        if name:
            node.setDisplayText(name)

        return node

    def addEdge(self, scene: InteractiveGraphScene, nid1=None, nid2=None):

        def defineEdgeStart():
            scene.selectionChanged.disconnect(defineEdgeStart)
            activeNode = scene.activeNode()
            if activeNode:
                activeNode.setState(NodeState.MARKED)
                self.addEdge(scene, nid1=activeNode.id)

        def defineEdgeEnd():
            activeNode = scene.activeNode()
            scene.selectionChanged.disconnect(defineEdgeEnd)
            if activeNode is None:
                self.addEdge(scene)
                return

            self.addEdge(scene, nid1, activeNode.id)

        if not nid1:
            activeNode = scene.activeNode()
            if activeNode:
                activeNode.setState(NodeState.MARKED)
                self.addEdge(scene, nid1=activeNode.id)
            else:
                scene.selectionChanged.connect(defineEdgeStart)
        elif not nid2:
            scene.selectionChanged.connect(defineEdgeEnd)
        else:
            node1 = scene.node(nid1)
            node1.setState(NodeState.DEFAULT)

            scene.newSceneArrow(nid1, nid2)
            self.edgeCreated_.emit(nid1)

    def addCrossEdge(self, scene: InteractiveGraphScene, nid1, nid2):
        scene.tuples[nid1].append(nid2)
        print(scene.tuples[nid1])
        self.crossEdgeCreated_.emit(nid1)
