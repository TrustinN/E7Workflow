from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Geometry:
    x: float
    y: float
    width: float
    height: float


@dataclass
class Color:
    r: int
    g: int
    b: int
    a: int = 255


@dataclass
class NodeItem:
    position: Optional[tuple[float, float]] = None
    color: Optional[Color] = None
    borderColor: Optional[Color] = None
    geometry: Optional[Geometry] = None
    padding: Optional[float] = 0.0
    displayText: Optional[str] = None
    iconPath: Optional[str] = None

    def deserialize(self, data: dict):
        for k, v in data.items():
            if k == "geometry" and v is not None:
                self.geometry = Geometry(**v)
            elif k in ("color", "borderColor") and v is not None:
                setattr(self, k, Color(**v))
            elif k == "position" and v is not None:
                self.position = tuple(v)
            else:
                setattr(self, k, v)


@dataclass
class EdgeItem:
    start: Optional[str] = None
    end: Optional[str] = None

    def deserialize(self, data: dict):
        self.start = data["start"]
        self.end = data["end"]


@dataclass
class GraphLayout:
    nodes: dict[str, NodeItem] = field(default_factory=dict)
    edges: dict[str, EdgeItem] = field(default_factory=dict)

    def deserialize(self, data):
        nodes = data["nodes"]
        for nodeID in nodes:
            item = NodeItem()
            item.deserialize(nodes[nodeID])
            self.nodes[nodeID] = item

        edges = data["edges"]
        for edgeID in edges:
            item = EdgeItem()
            item.deserialize(edges[edgeID])
            self.edges[edgeID] = item

    def clear(self):
        self.nodes.clear()
        self.edges.clear()
