from enum import Enum

from .manager import InventoryManager

SCOPE = "Penguin Scope"


class PenguinType(Enum):
    NEWBIE = ("Newbie", 6000)
    EXPERIENCED = ("Experienced", 18000)
    EPIC = ("Epic", 54000)

    def __init__(self, name, value):
        self._name = name
        self._value = value

    @property
    def name(self):
        return self._name

    @property
    def value(self):
        return self._value


penguinManager = InventoryManager(SCOPE, PenguinType)
