from dataclasses import dataclass
from enum import Enum, auto

import numpy as np
from PyQt5.QtCore import QObject, pyqtSignal


class RuntimeType(Enum):
    NONE = auto()
    NUM = auto()
    STR = auto()
    IMAGE = auto()


def inferType(value):
    if value is None:
        return RuntimeType.NONE

    if isinstance(value, (int, float)):
        return RuntimeType.NUM

    if isinstance(value, str):
        return RuntimeType.STR

    if isinstance(value, np.ndarray) or isinstance(value, list):
        return RuntimeType.IMAGE

    return RuntimeType.NONE


def valuesEqual(a, b) -> bool:
    if type(a) != type(b):
        return False

    if isinstance(a, np.ndarray):
        return np.array_equal(a, b)

    return a == b


@dataclass
class RuntimeSchema:
    name: str
    type: RuntimeType = RuntimeType.NONE
    value: None | float | str | np.ndarray = None

    @classmethod
    def fromData(cls, data):
        value = data["value"]
        rtype = RuntimeType[data["type"]]
        if rtype == RuntimeType.IMAGE and value is not None:
            value = np.array(value, dtype=np.uint8)

        return cls(
            name=data["name"],
            type=rtype,
            value=value,
        )

    def update(self, data: dict):
        if "value" in data:
            self.value = data["value"]
        if "type" in data:
            self.type = RuntimeType[data["type"]]
        if self.type == RuntimeType.IMAGE and self.value is not None:
            self.value = np.array(self.value, dtype=np.uint8)

    def toData(self):
        value = self.value
        if self.type == RuntimeType.IMAGE and value is not None:
            value = value.tolist()

        return {
            "name": self.name,
            "type": self.type.name,
            "value": value,
        }


class RuntimeModel(QObject):
    itemCreated = pyqtSignal(str)
    itemUpdated = pyqtSignal(str)
    itemDeleted = pyqtSignal(str)
    modelCleared = pyqtSignal()
    modelLoaded = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.variables: dict[str, RuntimeSchema] = {}

    def getItem(self, name: str) -> RuntimeSchema:
        return self.variables[name]

    def addItem(self, name: str, schema: RuntimeSchema):
        if name in self.variables:
            return

        self.variables[name] = schema
        self.itemCreated.emit(name)

    def updateItem(self, name: str, patch: dict):
        self.variables[name].update(patch)
        self.itemUpdated.emit(name)

    def update(self, patch: dict):
        for key, value in patch.items():
            if key in self.variables:

                schema = self.variables[key]
                if isinstance(value, dict):
                    schema.update(value)

                elif valuesEqual(schema.value, value):
                    continue
                else:
                    schema.value = value
                    schema.type = inferType(value)

                self.itemUpdated.emit(key)
                continue

            inferredType = inferType(value)
            schema = RuntimeSchema(
                name=key,
                type=inferredType,
                value=value,
            )

            self.variables[key] = schema
            self.itemCreated.emit(key)

    def deleteItem(self, name: str):
        if name in self.variables:
            self.variables.pop(name)
            self.itemDeleted.emit(name)

    def clear(self):
        self.variables.clear()
        self.modelCleared.emit()

    def toData(self) -> dict:
        return {k: v.toData() for k, v in self.variables.items()}

    def fromData(self, data):
        self.variables = {k: RuntimeSchema.fromData(v) for k, v in data.items()}
        self.modelLoaded.emit()
