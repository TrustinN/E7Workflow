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

    def getAction(self, nodeID: str) -> Optional[str]:
        return self.nodes.get(nodeID)

    def deleteAction(self, nodeID: str) -> str:
        if nodeID in self.nodes:
            return self.nodes.pop(nodeID)

        return None

    def setScript(self, edgeID: str, scriptID: str):
        self.edges[edgeID] = scriptID

    def getScript(self, edgeID: str) -> Optional[str]:
        return self.edges.get(edgeID)

    def deleteScript(self, edgeID: str) -> str:
        if edgeID in self.edges:
            return self.edges.pop(edgeID)

        return None

    def edgesFromScript(self, scriptID: str) -> list[str]:
        ret = []
        for edgeID, scrID in self.edges.items():
            if scrID == scriptID:
                ret.append(edgeID)
        return ret

    def setEntry(self, id: str):
        self.entry = id

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
        entry = data["entry"]

        for id, val in nodes.items():
            self.nodes[id] = val

        for id, val in edges.items():
            self.edges[id] = val

        self.entry = entry

        self.modelLoaded.emit()

    def clear(self):
        self.nodes.clear()
        self.edges.clear()
        self.entry = None

        self.modelCleared.emit()
