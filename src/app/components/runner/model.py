from dataclasses import asdict, dataclass
from typing import Optional

from PyQt5.QtCore import QObject, pyqtSignal


@dataclass
class RunnerNodeSchema:
    id: Optional[str] = None
    action: Optional[str] = None

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
class RunnerEdgeSchema:
    id: Optional[str] = None
    script: Optional[str] = None

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


class RunnerModel(QObject):
    modelCleared = pyqtSignal()
    modelLoaded = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.nodes: dict[str, RunnerNodeSchema] = {}
        self.edges: dict[str, RunnerEdgeSchema] = {}

        self.entry: str = None

    def setAction(self, nodeID: str, actionID: str):
        self.nodes[nodeID] = actionID

    def setScript(self, edgeID: str, scriptID: str):
        self.edges[edgeID] = scriptID

    def setEntry(self, id: str):
        self.entry = id

    def toData(self) -> dict:
        return {
            "nodes": {k: v.toData() for k, v in self.nodes.items()},
            "edges": {k: v.toData() for k, v in self.edges.items()},
            "entry": self.entry,
        }

    def fromData(self, data: dict):
        nodes = data["nodes"]
        edges = data["edges"]

        for id, node in nodes.items():
            self.nodes[id] = RunnerNodeSchema.fromData(node)

        for id, edge in edges.items():
            schema = RunnerEdgeSchema.fromData(edge)
            self.edges[id] = schema

        self.modelLoaded.emit()

    def clear(self):
        self.nodes.clear()
        self.edges.clear()
        self.entry = None

        self.modelCleared.emit()
