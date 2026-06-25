from dataclasses import asdict, dataclass, field
from typing import Optional

from nanoid import generate
from PyQt5.QtCore import QObject, pyqtSignal


@dataclass
class ActionSchema:
    name: Optional[str] = None
    systemParams: Optional[dict] = field(default_factory=dict)
    userParams: Optional[dict] = field(default_factory=dict)

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

    def copy(self):
        return ActionSchema.fromData(self.toData())


class ActionModel(QObject):
    modelCleared = pyqtSignal()
    modelLoaded = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.actions: dict[str, ActionSchema] = {}

    def createAction(self, schema: ActionSchema):
        id = generate()
        self.actions[id] = schema.copy()
        return id

    def setAction(self, id: str, schema: ActionSchema):
        self.actions[id] = schema

    def getAction(self, id: str) -> ActionSchema:
        return self.actions[id]

    def toData(self) -> dict:
        return {
            "actions": {k: v.toData() for k, v in self.actions.items()},
        }

    def clear(self):
        self.actions.clear()
        self.modelCleared.emit()

    def fromData(self, data):
        actions = data["actions"]
        for id, action in actions.items():
            self.actions[id] = ActionSchema.fromData(action)

        self.modelLoaded.emit()


class ActionViewModel(QObject):
    def __init__(self):
        super().__init__()

        self.draftAction: ActionSchema = None

    def setDraft(self, schema: ActionSchema):
        self.draftAction = schema

    def getDraft(self):
        return self.draftAction

    def clear(self):
        self.draftAction = None
