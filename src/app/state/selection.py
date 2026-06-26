from dataclasses import dataclass
from enum import Enum, auto

from PyQt5.QtCore import QObject, pyqtSignal


class SelectionType(Enum):
    NONE = auto()
    WORKSPACE = auto()
    EDGE = auto()


@dataclass
class Selection:
    id: str | None = None
    type: SelectionType = SelectionType.NONE

    def serialize(self):
        return {
            "id": self.id,
            "type": self.type.name if self.type else None,
        }

    @classmethod
    def deserialize(cls, state):
        return cls(
            id=state["id"],
            type=SelectionType[state["type"]] if state["type"] else None,
        )


class SelectionModel(QObject):
    selected_ = pyqtSignal(object)

    def __init__(self):
        super().__init__()

        self.previous = Selection()
        self.current = Selection()

    def setSelected(self, id, selectionType):
        if id == self.current.id and selectionType == self.current.type:
            return

        self.previous = Selection(self.current.id, self.current.type)
        self.current = Selection(id, selectionType)

        self.selected_.emit(self.current)

    def getSelected(self):
        return self.current

    def hasSelected(self):
        return self.current.id is not None

    def getPrevSelected(self):
        return self.previous

    def onItemDelete(self, id, selectionType):
        if id == self.current.id and selectionType == self.current.type:
            self.current = Selection()

        if id == self.previous.id and selectionType == self.previous.type:
            self.previous = Selection()

    def clearSelection(self):
        self.previous = Selection(self.current.id, self.current.type)
        self.current = Selection()

        self.selected_.emit(self.current)

    def clear(self):
        self.previous = Selection()
        self.current = Selection()
