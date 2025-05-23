import os

import cv2

from workflows.state.inventory.bookmark import BookmarkType
from workflows.state.inventory.penguin import PenguinType

ASSETS_PATH = "assets"


shopItemCnt = 6


bookmarkFilenames = ["cov_bm.png", "mys_bm.png", "frd_bm.png"]
bookmarkIconPaths = [os.path.join(ASSETS_PATH, fname) for fname in bookmarkFilenames]
bookmarkIcons = [cv2.imread(imPath) for imPath in bookmarkIconPaths]
bookmarkIcons = dict(zip(BookmarkType, bookmarkIcons))


def getBookMarkIcon(bType):
    return bookmarkIcons[bType]


penguinFilenames = ["nwb_pgn.png", "exp_pgn.png", "epc_pgn.png"]
penguinIconPaths = [os.path.join(ASSETS_PATH, fname) for fname in penguinFilenames]
penguinIcons = [cv2.imread(imPath) for imPath in penguinIconPaths]
penguinIcons = dict(zip(PenguinType, penguinIcons))


def getPenguinIcon(pType):
    return penguinIcons[pType]


digitsFilenames = [str(i) for i in range(10)]
digitsFilePaths = [
    os.path.join(ASSETS_PATH, "digits", f"{fname}.png") for fname in digitsFilenames
]
digitIcons = [cv2.imread(imPath, cv2.IMREAD_GRAYSCALE) for imPath in digitsFilePaths]


def getDigitIcon(digit):
    assert 0 <= digit and digit <= 9
    return digitIcons[digit]
