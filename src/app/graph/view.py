from functools import partial

from PyQt5.QtCore import QObject, QPointF, pyqtSignal

from .graph import GraphicsArrowItem, GraphicsNodeItem


class GraphView(QObject):
    nodeMoved_ = pyqtSignal(str, QPointF)
    nodePressed_ = pyqtSignal(str)

    def __init__(self, scene):
        super().__init__()
        self.scene = scene
        self.nodes: dict[str, GraphicsNodeItem] = {}
        self.edges: dict[any, GraphicsArrowItem] = {}

    def createNode(self, id):
        node = GraphicsNodeItem()
        self.nodes[id] = node

        onNodeMoved = partial(self.nodeMoved_.emit, id)
        onNodePressed = partial(self.nodePressed_.emit, id)

        node.emitter.onMove_.connect(onNodeMoved)
        node.emitter.onMousePress_.connect(onNodePressed)

        self.scene.addItem(node)

    def updateNode(self, id, data):
        node = self.nodes[id]

        pos = data.get("pos")
        text = data.get("text")
        color = data.get("color")

        if pos:
            node.setPos(pos)

        if text:
            node.setDisplayText(text)

        if color:
            node.setColor(color)

    def createEdge(self, id1, id2):
        key = (id1, id2)

        n1 = self.nodes[id1]
        n2 = self.nodes[id2]
        arrow = GraphicsArrowItem(n1.pos(), n2.pos())
        n1.emitter.onMove_.connect(arrow.setStart)
        n2.emitter.onMove_.connect(arrow.setEnd)

        self.edges[key] = arrow
        self.scene.addItem(arrow)

    def updateEdge(self, id1, id2, data):
        pass
