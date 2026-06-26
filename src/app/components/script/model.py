from dataclasses import asdict, dataclass
from typing import Optional

from PyQt5.QtCore import QObject, pyqtSignal


@dataclass
class ScriptSchema:
    name: Optional[str] = None
    code: Optional[str] = None

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


class ScriptModel(QObject):
    scriptUpdated = pyqtSignal(str)
    modelCleared = pyqtSignal()
    modelLoaded = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.scripts: dict[str, ScriptSchema] = {}

    def addScript(self, id: str, schema: ScriptSchema):
        self.scripts[id] = schema

    def getScript(self, id: str):
        return self.scripts[id]

    def updateScript(self, id: str, patch: dict):
        self.scripts[id].update(patch)
        self.scriptUpdated.emit(id)

    def getScripts(self) -> list[str]:
        return list(self.scripts.keys())

    def toData(self) -> dict:
        return {"scripts": {k: v.toData() for k, v in self.scripts.items()}}

    def clear(self):
        self.scripts.clear()
        self.modelCleared.emit()

    def fromData(self, data):
        scripts = data["scripts"]
        for id, script in scripts.items():
            self.scripts[id] = ScriptSchema.fromData(script)

        self.modelLoaded.emit()

    def uniqueName(self, name):
        schemas = list(self.scripts.values())
        existing = {s.name for s in schemas}

        if name not in existing:
            return name

        i = 2
        while f"{name} ({i})" in existing:
            i += 1

        return f"{name} ({i})"


class ScriptViewModel(QObject):
    def __init__(self):
        super().__init__()

        self.activeScript: str = None

    def setActiveScript(self, id):
        self.activeScript = id

    def getActiveScript(self):
        return self.activeScript
