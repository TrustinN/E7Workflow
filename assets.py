import os
from enum import Enum

import cv2

ASSETS_PATH = "assets"


shopItemCnt = 6


# Bookmark assets
class BookmarkType(Enum):
    COVENANT = ("Covenant", 5)
    MYSTIC = ("Mystic", 10)
    FRIENDSHIP = ("Friendship", 3)

    def __init__(self, name, cost):
        self._name = name
        self._cost = cost

    @property
    def name(self):
        return self._name

    @property
    def cost(self):
        return self._cost


bookmarkTypes = [bookmark for bookmark in BookmarkType]
bookmarkFilenames = ["cov_bm.png", "mys_bm.png", "frd_bm.png"]
bookmarkIconPaths = [os.path.join(ASSETS_PATH, fname) for fname in bookmarkFilenames]
bookmarkIcons = [cv2.imread(imPath) for imPath in bookmarkIconPaths]
bookmarkIcons = dict(zip(bookmarkTypes, bookmarkIcons))


def getBookMarkIcon(bType):
    return bookmarkIcons[bType]


# Currency
class CurrencyType(Enum):
    GOLD = "Gold"
    SKYSTONES = "Skystones"

    def __init__(self, name):
        self._name = name

    @property
    def name(self):
        return self._name


currencyTypes = [currency for currency in CurrencyType]


# Penguins
class PenguinTypes(Enum):
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


penguinTypes = [pType for pType in PenguinTypes]
penguinFilenames = ["nwb_pgn.png", "exp_pgn.png", "epc_pgn.png"]
penguinIconPaths = [os.path.join(ASSETS_PATH, fname) for fname in penguinFilenames]
penguinIcons = [cv2.imread(imPath) for imPath in penguinIconPaths]
penguinIcons = dict(zip(penguinTypes, penguinIcons))


def getPenguinIcon(pType):
    return penguinIcons[pType]
