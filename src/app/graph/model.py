from dataclasses import dataclass, field
from functools import partial
from typing import Optional

from PyQt5.QtCore import QObject, QPointF, QRectF, pyqtSignal
from PyQt5.QtGui import QColor


@dataclass
class NodeData:
    pos: QPointF = field(default_factory=QPointF)
    text: Optional[str] = None
    color: Optional[QColor] = None
    rect: QRectF = field(default_factory=lambda: QRectF(0, 0, 50, 50))


@dataclass
class EdgeData:
    color: Optional[QColor] = None
    posTail: Optional[QPointF] = None
    posHead: Optional[QPointF] = None


@dataclass
class GraphData:
    nodes: list[str] = field(default_factory=list)
    edges: dict[str, list[str]] = field(default_factory=dict)
    edgesReversed: dict[str, list[str]] = field(default_factory=dict)

    nodeSelected: Optional[str] = None


class NodeModel(QObject):
    dataChanged_ = pyqtSignal()

    def __init__(self, data: NodeData = None):
        super().__init__()

        if data:
            self.data = data
        else:
            self.data: NodeData = NodeData()

    def update(self, data: NodeData):
        if data.pos is not None:
            self.data.pos = data.pos

        if data.text is not None:
            self.data.text = data.text

        if data.color is not None:
            self.data.color = data.color

        if data.rect is not None:
            self.data.rect = data.rect

        self.dataChanged_.emit()


class EdgeModel(QObject):
    dataChanged_ = pyqtSignal()

    def __init__(self, data: EdgeData = None):
        super().__init__()

        if data:
            self.data = data
        else:
            self.data: EdgeData = EdgeData()

    def update(self, data: EdgeData):
        if data.color is not None:
            self.data.color = data.color

        if data.posHead is not None:
            self.data.posHead = data.posHead

        if data.posTail is not None:
            self.data.posTail = data.posTail

        self.dataChanged_.emit()


class GraphModel(QObject):
    nodeCreated_ = pyqtSignal(str, NodeData)
    nodeUpdated_ = pyqtSignal(str, NodeData)

    edgeCreated_ = pyqtSignal(str, str, EdgeData)
    edgeUpdated_ = pyqtSignal(str, str, EdgeData)

    dataChanged_ = pyqtSignal(GraphData)

    def __init__(self):
        super().__init__()

        self.data = GraphData()

        self.nodeModels: dict[str, NodeModel] = {}
        self.edgeModels: dict[tuple[str, str], EdgeModel] = {}

    def createNode(self, id):
        self.data.nodes.append(id)

        nodeModel = NodeModel()
        onDataChanged = partial(self.nodeUpdated_.emit, id, nodeModel.data)
        nodeModel.dataChanged_.connect(onDataChanged)

        self.nodeModels[id] = nodeModel
        self.nodeCreated_.emit(id, nodeModel.data)

    def updateNode(self, id, data: NodeData):
        nodeModel = self.nodeModels.get(id)
        nodeModel.update(data)

    def createEdge(self, id1, id2):
        self.data.edges.setdefault(id1, []).append(id2)
        self.data.edgesReversed.setdefault(id2, []).append(id1)

        key = (id1, id2)
        edgeModel = EdgeModel()
        onEdgeChanged = partial(self.edgeUpdated_.emit, id1, id2, edgeModel.data)
        edgeModel.dataChanged_.connect(onEdgeChanged)
        self.edgeModels[key] = edgeModel
        self.edgeCreated_.emit(id1, id2, edgeModel.data)

    def updateEdge(self, id1, id2, data: EdgeData):
        key = (id1, id2)
        edgeModel = self.edgeModels.get(key)
        edgeModel.update(data)

    def setSelectedNode(self, id):
        self.data.nodeSelected = id
        self.dataChanged_.emit(self.data)

    def selectedNode(self):
        return self.data.nodeSelected
