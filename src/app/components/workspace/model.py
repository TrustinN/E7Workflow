from dataclasses import asdict, dataclass, field
from typing import Optional, Union

from PyQt5.QtCore import QObject, pyqtSignal

from src.app.state.layouts.graph import Color, Geometry


@dataclass
class WorkspaceSchema:
    displayText: Optional[str] = None
    geometry: Optional[Geometry] = None
    iconPath: Optional[str] = None
    padding: Optional[int] = None
    color: Optional[Color] = None
    borderColor: Optional[Color] = None
    grouping: Optional[str] = None

    children: list[str] = field(default_factory=list)
    parent: Optional[str] = None

    @classmethod
    def fromData(cls, data: dict):
        schema = cls()
        schema.update(data)
        return schema

    def update(self, data: Union["WorkspaceSchema", dict]):
        if isinstance(data, WorkspaceSchema):
            data = data.toData()

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

    def __init__(self):
        super().__init__()

        self.nodes: dict[str, WorkspaceSchema] = {}
        self.root: str = None

    def getItem(self, id: str) -> WorkspaceSchema:
        return self.nodes[id]

    def addItem(
        self,
        id: str,
        schema: Union[WorkspaceSchema, dict],
        parentID: str = None,
    ):
        if isinstance(schema, dict):
            schema = WorkspaceSchema.fromData(schema)

        self.nodes[id] = schema
        if parentID is None:
            self.root = id
        else:
            schema.parent = parentID
            self.nodes[parentID].children.append(id)

        self.modelCreated.emit(id)

    def updateItem(self, id: str, schema: Union[WorkspaceSchema, dict]):
        self.nodes[id].update(schema)
        self.modelUpdated.emit(id)
