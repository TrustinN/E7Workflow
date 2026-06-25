from dataclasses import asdict, dataclass
from typing import Optional

from PyQt5.QtCore import QObject, pyqtSignal


class RunnerModel(QObject):
    modelCleared = pyqtSignal()
    modelLoaded = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.nodes: dict[str, str] = {}
        self.edges: dict[str, str] = {}

        self.entry: str = None

    def setAction(self, nodeID: str, actionID: str):
        self.nodes[nodeID] = actionID

    def setScript(self, edgeID: str, scriptID: str):
        self.edges[edgeID] = scriptID

    def setEntry(self, id: str):
        self.entry = id

    def getAction(self, nodeID: str) -> Optional[str]:
        return self.nodes.get(nodeID)

    def getScript(self, edgeID: str) -> Optional[str]:
        return self.edges.get(edgeID)

    def getEntry(self) -> Optional[str]:
        return self.entry

    def toData(self) -> dict:
        return {
            "nodes": self.nodes,
            "edges": self.edges,
            "entry": self.entry,
        }

    def fromData(self, data: dict):
        nodes = data["nodes"]
        edges = data["edges"]

        for id, val in nodes.items():
            self.nodes[id] = val

        for id, val in edges.items():
            self.edges[id] = val

        self.modelLoaded.emit()

    def clear(self):
        self.nodes.clear()
        self.edges.clear()
        self.entry = None

        self.modelCleared.emit()
