from collections import defaultdict
from dataclasses import asdict, dataclass, field
from typing import Optional, Union

from PyQt5.QtCore import QObject, pyqtSignal

from src.app.state.layouts.graph import Color, Geometry


@dataclass
class NodeSchema:
    id: Optional[str] = None

    displayText: Optional[str] = None
    geometry: Optional[Geometry] = None
    shape: Optional[str] = None
    position: Optional[tuple[float, float]] = None
    color: Optional[Color] = None
    borderColor: Optional[Color] = None

    children: list[str] = field(default_factory=list)
    parent: Optional[str] = None

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


class GraphModel(QObject):
    nodeCreated = pyqtSignal(str)
    nodeUpdated = pyqtSignal(str)

    edgeCreated = pyqtSignal(str)
    edgeUpdated = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.nodes: dict[str, NodeSchema] = {}
        self.edges: dict[str, EdgeSchema] = {}

        self.adjacency: dict[str, set] = defaultdict(set)

    def parent(self, id: str):
        return self.nodes[id].parent

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
