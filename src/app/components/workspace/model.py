from dataclasses import asdict, dataclass, field
from typing import Optional, Union

from PyQt5.QtCore import QObject, pyqtSignal

from src.app.state import Color, Geometry


@dataclass
class WorkspaceSchema:
    id: Optional[str] = None
    name: Optional[str] = None
    grouping: Optional[str] = None

    displayText: Optional[str] = None
    geometry: Optional[Geometry] = None
    iconPath: Optional[str] = None
    padding: Optional[int] = None
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


class WorkspaceModel(QObject):
    modelCreated = pyqtSignal(str)
    modelUpdated = pyqtSignal(str)
    modelDeleted = pyqtSignal(str)
    modelCleared = pyqtSignal()
    modelLoaded = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.nodes: dict[str, WorkspaceSchema] = {}
        self.root: str = None

        self.availableGroups = set(chr(ord("A") + i) for i in range(26))
        self.groupAssignments = {}

    def popGroup(self):
        group = min(self.availableGroups)
        self.availableGroups.remove(group)
        return group

    def assignGroup(self, id, parentID):
        group = None
        if self.rootIndex() == parentID:
            group = self.popGroup()
            self.groupAssignments[id] = group

        else:
            group = self.groupAssignments[parentID]
            self.groupAssignments[id] = group

        return group

    def rootIndex(self) -> str:
        return self.root

    def workspaces(self) -> list[str]:
        return list(self.nodes.keys())

    def parent(self, id: str) -> str:
        return self.nodes[id].parent

    def getItem(self, id: str) -> WorkspaceSchema:
        return self.nodes[id]

    def addItem(
        self,
        id: str,
        schema: Union[WorkspaceSchema, dict],
    ):
        if isinstance(schema, dict):
            schema = WorkspaceSchema.fromData(schema)

        self.nodes[id] = schema
        parentID = schema.parent
        if parentID is None:
            self.root = id
        else:
            self.nodes[parentID].children.append(id)
            schema.grouping = self.assignGroup(id, parentID)

        schema.displayText = schema.name
        if schema.grouping:
            schema.displayText = f"{schema.grouping} - {schema.name}"

        self.modelCreated.emit(id)

    def removeItem(self, id: str):
        if id not in self.nodes:
            return

        schema = self.getItem(id)
        if schema.parent:
            parent = self.getItem(schema.parent)
            parent.children.remove(id)

        while schema.children:
            self.removeItem(schema.children[0])

        self.nodes.pop(id)

        self.modelDeleted.emit(id)

    def updateItem(self, id: str, patch: dict):
        self.nodes[id].update(patch)
        self.modelUpdated.emit(id)

    def toData(self):
        return {
            "nodes": {k: v.toData() for k, v in self.nodes.items()},
            "root": self.root,
        }

    def fromData(self, data):
        nodes = data["nodes"]
        root = data["root"]

        self.root = root
        for id, node in nodes.items():
            schema = WorkspaceSchema.fromData(node)
            self.nodes[id] = schema

            if id == self.rootIndex():
                continue

            grouping = schema.grouping
            self.groupAssignments[id] = grouping
            self.availableGroups.discard(grouping)

        self.modelLoaded.emit()

    def clear(self):
        self.nodes.clear()
        self.root = None

        self.availableGroups = set(chr(ord("A") + i) for i in range(26))
        self.groupAssignments = {}

        self.modelCleared.emit()
