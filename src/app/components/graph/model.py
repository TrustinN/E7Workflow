from collections import defaultdict
from dataclasses import asdict, dataclass, field
from typing import Optional, Union

from PyQt5.QtCore import QObject, pyqtSignal

from src.app.state.layouts.graph import Color, Geometry


@dataclass
class NodeSchema:
    id: Optional[str] = None

    name: Optional[str] = None
    group: Optional[str] = None

    children: list[str] = field(default_factory=list)
    parent: Optional[str] = None

    @classmethod
    def fromData(cls, data: dict):
        schema = cls()
        schema.update(data)
        return schema

    def update(self, data: dict):
        for k, v in data.items():
            setattr(self, k, v)

    def toData(self) -> dict:
        return asdict(self)


@dataclass
class NodeViewState:
    displayText: Optional[str] = None
    geometry: Optional[Geometry] = None
    shape: Optional[str] = None
    position: Optional[tuple[float, float]] = None
    color: Optional[Color] = None
    borderColor: Optional[Color] = None
    visible: Optional[bool] = None

    @classmethod
    def fromData(cls, data: dict):
        schema = cls()
        schema.update(data)
        return schema

    def update(self, data: dict):
        for k, v in data.items():
            if k == "geometry":
                self.geometry = Geometry(**v) if isinstance(v, dict) else v
            elif k in ("color", "borderColor"):
                setattr(self, k, Color(**v) if isinstance(v, dict) else v)
            else:
                setattr(self, k, v)

    def toData(self) -> dict:
        return asdict(self)


@dataclass
class EdgeSchema:
    id: Optional[str] = None

    source: Optional[str] = None
    target: Optional[str] = None

    @classmethod
    def fromData(cls, data: dict):
        schema = cls()
        schema.update(data)
        return schema

    def update(self, data: dict):
        for k, v in data.items():
            setattr(self, k, v)

    def toData(self) -> dict:
        return asdict(self)


@dataclass
class EdgeViewState:
    visible: Optional[bool] = None

    @classmethod
    def fromData(cls, data: dict):
        schema = cls()
        schema.update(data)
        return schema

    def update(self, data: dict):
        for k, v in data.items():
            setattr(self, k, v)

    def toData(self) -> dict:
        return asdict(self)


class GraphModel(QObject):
    nodeCreated = pyqtSignal(str)
    nodeUpdated = pyqtSignal(str)

    edgeCreated = pyqtSignal(str)
    edgeUpdated = pyqtSignal(str)

    modelCleared = pyqtSignal()
    modelLoaded = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.nodes: dict[str, NodeSchema] = {}
        self.edges: dict[str, EdgeSchema] = {}

        self.adjacency: dict[str, set] = defaultdict(set)

    def nodeList(self) -> list[str]:
        return list(self.nodes.keys())

    def edgeList(self) -> list[str]:
        return list(self.edges.keys())

    def parentNode(self, id: str) -> str:
        return self.getNode(id).parent

    def parentEdge(self, id: str) -> str:
        edge = self.getEdge(id)
        return self.parentNode(edge.source)

    def getNode(self, id: str) -> NodeSchema:
        return self.nodes[id]

    def getEdge(self, id: str) -> EdgeSchema:
        return self.edges[id]

    def getNodeEdges(self, id: str) -> set[str]:
        return self.adjacency[id]

    def addNode(self, id: str, schema: Union[NodeSchema, dict]):
        if isinstance(schema, dict):
            schema = NodeSchema.fromData(schema)

        self.nodes[id] = schema
        parentID = schema.parent
        if parentID:
            self.nodes[parentID].children.append(id)

        self.nodeCreated.emit(id)

    def addEdge(self, id: str, schema: Union[EdgeSchema, dict]):
        if isinstance(schema, dict):
            schema = EdgeSchema.fromData(schema)

        self.edges[id] = schema
        self.adjacency[schema.source].add(id)
        self.edgeCreated.emit(id)

    def updateNode(self, id: str, patch: dict):
        self.nodes[id].update(patch)
        self.nodeUpdated.emit(id)

    def updateEdge(self, id: str, patch: dict):
        self.edges[id].update(patch)
        self.edgeUpdated.emit(id)

    def getComponentNodes(self, id: str) -> list[str]:
        return list(self.nodes[id].children)

    def getComponentEdges(self, id: str) -> list[str]:
        edges = []

        for node in self.getComponentNodes(id):
            for edge in self.getNodeEdges(node):
                if not self.isCrossEdge(edge):
                    edges.append(edge)

        return edges

    def isCrossEdge(self, id: str) -> bool:
        edge = self.getEdge(id)
        source = self.getNode(edge.source)
        target = self.getNode(edge.target)
        return source.parent != target.parent

    def toData(self) -> dict:
        return {
            "nodes": {k: v.toData() for k, v in self.nodes.items()},
            "edges": {k: v.toData() for k, v in self.edges.items()},
        }

    def fromData(self, data: dict):
        nodes = data["nodes"]
        edges = data["edges"]

        for id, node in nodes.items():
            self.nodes[id] = NodeSchema.fromData(node)

        for id, edge in edges.items():
            schema = EdgeSchema.fromData(edge)
            self.edges[id] = schema
            source = schema.source
            self.adjacency[source].add(id)

        self.modelLoaded.emit()

    def clear(self):
        self.nodes.clear()
        self.edges.clear()
        self.adjacency.clear()

        self.modelCleared.emit()


class GraphViewState(QObject):
    nodeCreated = pyqtSignal(str)
    nodeUpdated = pyqtSignal(str)

    edgeCreated = pyqtSignal(str)
    edgeUpdated = pyqtSignal(str)

    modelCleared = pyqtSignal()
    modelLoaded = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.nodes: dict[str, NodeViewState] = {}
        self.edges: dict[str, EdgeViewState] = {}

    def addNode(self, id, state):
        self.nodes[id] = state
        self.nodeCreated.emit(id)

    def addEdge(self, id, state):
        self.edges[id] = state
        self.edgeCreated.emit(id)

    def getNode(self, id):
        return self.nodes[id]

    def getEdge(self, id):
        return self.edges[id]

    def updateNode(self, id, state):
        self.nodes[id].update(state)
        self.nodeUpdated.emit(id)

    def updateEdge(self, id, state):
        self.edges[id].update(state)
        self.edgeUpdated.emit(id)

    def toData(self) -> dict:
        return {
            "nodes": {k: v.toData() for k, v in self.nodes.items()},
            "edges": {k: v.toData() for k, v in self.edges.items()},
        }

    def fromData(self, data: dict):
        nodes = data["nodes"]
        edges = data["edges"]

        for id, node in nodes.items():
            self.nodes[id] = NodeViewState.fromData(node)

        for id, edge in edges.items():
            self.edges[id] = EdgeViewState.fromData(edge)

        self.modelLoaded.emit()

    def clear(self):
        self.nodes.clear()
        self.edges.clear()

        self.modelCleared.emit()


class GraphDocument:
    def __init__(self, model: GraphModel):
        self.model = model

        self.viewStates: dict[str, GraphViewState] = {}

    def addViewState(self, id, viewState: GraphViewState):
        self.viewStates[id] = viewState

    def layout(self, id):
        return self.viewStates[id]
