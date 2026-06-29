from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Optional

from PyQt5.QtCore import QObject, pyqtSignal

BASE_DIR = Path(__file__).resolve().parent


def loadPreAction():
    path = Path(__file__).resolve().parent / "pre.py"
    return path.read_text(encoding="utf-8")


def loadPostAction():
    path = Path(__file__).resolve().parent / "post.py"
    return path.read_text(encoding="utf-8")


@dataclass
class RunnerNodeSchema:
    actionID: Optional[str] = None
    preAction: str = field(default_factory=lambda: loadPreAction())
    postAction: str = field(default_factory=lambda: loadPostAction())

    @classmethod
    def fromData(cls, data: dict):
        return cls(**data)

    def update(self, data: dict):
        for k, v in data.items():
            setattr(self, k, v)

    def toData(self) -> dict:
        return asdict(self)


@dataclass
class RunnerEdgeSchema:
    scriptID: Optional[str] = None
    priority: int = 0

    @classmethod
    def fromData(cls, data: dict):
        return cls(**data)

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

        self.entry: Optional[str] = None

    def setNode(self, nodeID: str, schema: RunnerNodeSchema):
        self.nodes[nodeID] = schema

    def updateNode(self, nodeID: str, patch: dict):
        self.nodes[nodeID].update(patch)

    def getNode(self, nodeID: str) -> RunnerNodeSchema:
        return self.nodes.get(nodeID)

    def deleteNode(self, nodeID: str) -> RunnerNodeSchema:
        if nodeID in self.nodes:
            return self.nodes.pop(nodeID)

        return None

    def setEdge(self, edgeID: str, schema: RunnerEdgeSchema):
        self.edges[edgeID] = schema

    def getEdge(self, edgeID: str) -> RunnerEdgeSchema:
        return self.edges.get(edgeID)

    def updateEdge(self, edgeID: str, patch: dict):
        self.edges[edgeID].update(patch)

    def deleteEdge(self, edgeID: str) -> RunnerEdgeSchema:
        if edgeID in self.edges:
            return self.edges.pop(edgeID)

        return None

    def edgesFromScript(self, scriptID: str) -> list[str]:
        ret = []
        for edgeID, schema in self.edges.items():
            if schema.scriptID == scriptID:
                ret.append(edgeID)
        return ret

    def setEntry(self, id: str):
        self.entry = id

    def getEntry(self) -> Optional[str]:
        return self.entry

    def toData(self):
        return {
            "nodes": {k: v.toData() for k, v in self.nodes.items()},
            "edges": {k: v.toData() for k, v in self.edges.items()},
            "entry": self.entry,
        }

    def fromData(self, data):
        self.nodes = {k: RunnerNodeSchema.fromData(v) for k, v in data["nodes"].items()}
        self.edges = {k: RunnerEdgeSchema.fromData(v) for k, v in data["edges"].items()}
        self.entry = data["entry"]

        self.modelLoaded.emit()

    def clear(self):
        self.nodes.clear()
        self.edges.clear()
        self.entry = None

        self.modelCleared.emit()
