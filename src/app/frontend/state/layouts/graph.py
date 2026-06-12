from dataclasses import dataclass


@dataclass
class NodeItem:
    position: tuple[float, float]
    color: tuple[int, int, int]
    borderColor: tuple[int, int, int]
    geometry: tuple[float, float, float, float]
    displayText: str


@dataclass
class EdgeItem:
    start: str
    end: str


class GraphLayout:
    def __init__(self):
        super().__init__()

        self.nodes: dict[str, NodeItem] = {}
        self.edges: dict[str, EdgeItem] = {}

    def setNodeData(self, id: str, data: NodeItem):
        self.nodes[id] = data

    def getNodeData(self, id: str) -> NodeItem:
        return self.nodes[id]

    def setEdgeData(self, id: str, data: EdgeItem):
        self.edges[id] = data

    def getEdgeData(self, id: str) -> EdgeItem:
        return self.edges[id]
