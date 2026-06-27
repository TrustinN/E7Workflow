from collections import defaultdict
from dataclasses import asdict, dataclass, field
from typing import Optional, Union

from PyQt5.QtCore import QObject, pyqtSignal

from src.app.state import Color


class NodeType:
    RECTANGLE = "Rectangle"
    CIRCLE = "Circle"


@dataclass
class NodeSchema:
    id: str
    name: str

    group: Optional[str] = None

    @classmethod
    def fromData(cls, data: dict):
        return cls(**data)

    def update(self, data: dict):
        for k, v in data.items():
            setattr(self, k, v)

    def toData(self) -> dict:
        return asdict(self)


@dataclass
class NodeViewState:
    displayText: str = ""
    shape: str = "Rectangle"
    position: tuple[float, float] = (0.0, 0.0)
    color: Color = field(default_factory=lambda: Color(r=20, g=20, b=20))
    borderColor: Color = field(default_factory=lambda: Color(r=255, b=255, g=255))
    visible: bool = True

    @classmethod
    def fromData(cls, data: dict):
        schema = cls()
        schema.update(data)
        return schema

    def update(self, data: dict):
        for k, v in data.items():
            if k in ("color", "borderColor"):
                setattr(self, k, Color(**v) if isinstance(v, dict) else v)
            else:
                setattr(self, k, v)

    def toData(self) -> dict:
        return asdict(self)


@dataclass
class EdgeSchema:
    id: str

    source: str
    target: str

    @classmethod
    def fromData(cls, data: dict):
        return cls(**data)

    def update(self, data: dict):
        for k, v in data.items():
            setattr(self, k, v)

    def toData(self) -> dict:
        return asdict(self)


@dataclass
class EdgeViewState:
    visible: bool = True
    label: str = ""

    @classmethod
    def fromData(cls, data: dict):
        return cls(**data)

    def update(self, data: dict):
        for k, v in data.items():
            setattr(self, k, v)

    def toData(self) -> dict:
        return asdict(self)


class GraphModel(QObject):
    nodeCreated = pyqtSignal(str)
    nodeUpdated = pyqtSignal(str)
    nodeDeleted = pyqtSignal(str)

    edgeCreated = pyqtSignal(str)
    edgeUpdated = pyqtSignal(str)
    edgeDeleted = pyqtSignal(str)

    modelCleared = pyqtSignal()
    modelLoaded = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.nodes: dict[str, NodeSchema] = {}
        self.edges: dict[str, EdgeSchema] = {}

        self.adjacency: dict[str, set] = defaultdict(set)
        self.adjacencyC: dict[str, set] = defaultdict(set)

        self.parent: dict[str, str] = {}
        self.children: dict[str, set[str]] = defaultdict(set)

    def nodeList(self) -> list[str]:
        return list(self.nodes.keys())

    def edgeList(self) -> list[str]:
        return list(self.edges.keys())

    def parentNode(self, id: str) -> str:
        return self.parent.get(id)

    def parentEdge(self, id: str) -> str:
        edge = self.getEdge(id)
        return self.parentNode(edge.source)

    def getNode(self, id: str) -> NodeSchema:
        return self.nodes[id]

    def getEdge(self, id: str) -> EdgeSchema:
        return self.edges[id]

    def getNodeEdges(self, id: str) -> set[str]:
        return self.adjacency[id]

    def addNode(
        self, id: str, parentID: Optional[str], schema: Union[NodeSchema, dict]
    ):
        if isinstance(schema, dict):
            schema = NodeSchema.fromData(schema)

        self.nodes[id] = schema
        self.parent[id] = parentID
        if parentID:
            self.children[parentID].add(id)

        self.nodeCreated.emit(id)

    def addEdge(self, id: str, schema: Union[EdgeSchema, dict]):
        if isinstance(schema, dict):
            schema = EdgeSchema.fromData(schema)

        self.edges[id] = schema
        self.adjacency[schema.source].add(id)
        self.adjacencyC[schema.target].add(id)
        self.edgeCreated.emit(id)

    def updateNode(self, id: str, patch: dict):
        self.nodes[id].update(patch)
        self.nodeUpdated.emit(id)

    def updateEdge(self, id: str, patch: dict):
        self.edges[id].update(patch)
        self.edgeUpdated.emit(id)

    def deleteNode(self, id):
        parent = self.parent.get(id)
        if parent:
            self.children[parent].remove(id)

        for child in self.children[id]:
            self.parent[child] = None

        self.parent.pop(id, None)
        self.children.pop(id, None)

        for edge in list(self.adjacency[id]):
            self.deleteEdge(edge)

        for edge in list(self.adjacencyC[id]):
            self.deleteEdge(edge)

        self.nodes.pop(id)
        self.nodeDeleted.emit(id)

    def deleteEdge(self, id: str):
        if id not in self.edges:
            return

        edge = self.getEdge(id)
        source = edge.source
        target = edge.target

        self.adjacency[source].remove(id)
        self.adjacencyC[target].remove(id)

        self.edges.pop(id)
        self.edgeDeleted.emit(id)

    def getComponentNodes(self, id: str) -> list[str]:
        return list(self.children[id])

    def getComponentEdges(self, id: str) -> list[str]:
        edges = []

        for node in self.getComponentNodes(id):
            for edge in self.getNodeEdges(node):
                if not self.isCrossEdge(edge):
                    edges.append(edge)

        return edges

    def isCrossEdge(self, id: str) -> bool:
        edge = self.getEdge(id)
        return self.parentNode(edge.source) != self.parentNode(edge.target)

    def toData(self) -> dict:
        return {
            "nodes": {k: v.toData() for k, v in self.nodes.items()},
            "edges": {k: v.toData() for k, v in self.edges.items()},
            "parent": self.parent,
        }

    def fromData(self, data: dict):
        nodes = data["nodes"]
        edges = data["edges"]
        parent = data["parent"]

        for id, node in nodes.items():
            self.nodes[id] = NodeSchema.fromData(node)

        for id, edge in edges.items():
            schema = EdgeSchema.fromData(edge)
            self.edges[id] = schema
            self.adjacency[schema.source].add(id)
            self.adjacencyC[schema.target].add(id)

        self.parent = parent
        self.children = defaultdict(set)
        for child, parent in self.parent.items():
            if parent is not None:
                self.children[parent].add(child)

        self.modelLoaded.emit()

    def clear(self):
        self.nodes.clear()
        self.edges.clear()
        self.adjacency.clear()
        self.adjacencyC.clear()
        self.parent.clear()
        self.children.clear()

        self.modelCleared.emit()


class GraphViewState(QObject):
    nodeCreated = pyqtSignal(str)
    nodeUpdated = pyqtSignal(str)
    nodeDeleted = pyqtSignal(str)

    edgeCreated = pyqtSignal(str)
    edgeUpdated = pyqtSignal(str)
    edgeDeleted = pyqtSignal(str)

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

    def deleteNode(self, id):
        self.nodes.pop(id)
        self.nodeDeleted.emit(id)

    def deleteEdge(self, id):
        self.edges.pop(id)
        self.edgeDeleted.emit(id)

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
