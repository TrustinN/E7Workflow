from enum import Enum

from .manager import InventoryManager

SCOPE = "Bookmark Scope"


class BookmarkType(Enum):
    COVENANT = ("Covenant", 184000)
    MYSTIC = ("Mystic", 280000)
    # FRIENDSHIP = ("Friendship", 18000)

    def __init__(self, name, cost):
        self._name = name
        self._cost = cost

    @property
    def name(self):
        return self._name

    @property
    def cost(self):
        return self._cost


bookmarkManager = InventoryManager(SCOPE, BookmarkType)
