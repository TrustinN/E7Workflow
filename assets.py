import os
from enum import Enum

import cv2
import skimage.io as skio

ASSETS_PATH = "assets"
BOOKMARK_DIR = "bookmarks"
PENGUIN_DIR = "penguins"
DIGITS_DIR = "digits"


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


bookmarkFilenames = [f"{bType.name}.png" for bType in BookmarkType]
bookmarkIconPaths = [
    os.path.join(ASSETS_PATH, BOOKMARK_DIR, fname) for fname in bookmarkFilenames
]
bookmarkIcons = [cv2.imread(imPath) for imPath in bookmarkIconPaths]
bookmarkIcons = [cv2.cvtColor(icon, cv2.COLOR_BGR2RGB) for icon in bookmarkIcons]
bookmarkIcons = dict(zip(BookmarkType, bookmarkIcons))


def getBookMarkIcon(bType):
    return bookmarkIcons[bType]


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


penguinFilenames = [f"{pType.name}.png" for pType in PenguinType]
penguinIconPaths = [
    os.path.join(ASSETS_PATH, PENGUIN_DIR, fname) for fname in penguinFilenames
]
penguinIcons = [cv2.imread(imPath, cv2.COLOR_BGR2RGB) for imPath in penguinIconPaths]
penguinIcons = [cv2.cvtColor(icon, cv2.COLOR_BGR2RGB) for icon in penguinIcons]
penguinIcons = dict(zip(PenguinType, penguinIcons))


def getPenguinIcon(pType):
    return penguinIcons[pType]


class CurrencyType(Enum):
    GOLD = "Gold"
    SKYSTONE = "Skystone"


digitsFilenames = [str(i) for i in range(10)]
digitsFilePaths = [
    os.path.join(ASSETS_PATH, DIGITS_DIR, f"{fname}.png") for fname in digitsFilenames
]
digitIcons = [cv2.imread(imPath, cv2.IMREAD_GRAYSCALE) for imPath in digitsFilePaths]


def getDigitIcon(digit):
    assert 0 <= digit and digit <= 9
    return digitIcons[digit]
