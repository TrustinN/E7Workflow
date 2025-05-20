import os

import cv2

ASSETS_PATH = "assets"

# Bookmark assets
bookmarkFilenames = ["cov_bm.png", "mys_bm.png", "frd_bm.png"]
bookmarkIconPaths = [os.path.join(ASSETS_PATH, fname) for fname in bookmarkFilenames]
bookmarkIcons = [cv2.imread(imPath) for imPath in bookmarkIconPaths]

buttonFilenames = ["buy_btn.png", "refresh_btn.png"]
buttonFilePaths = [os.path.join(ASSETS_PATH, fname) for fname in buttonFilenames]
buttonIcons = [cv2.imread(imPath) for imPath in buttonFilePaths]

buyBtn = buttonIcons[0]
refreshBtn = buttonIcons[1]

shopItemCnt = 6


class BookmarkType:
    COVENANT = 0
    MYSTIC = 1
    FRIENDSHIP = 2


def getBookMarkIcon(bType):
    return bookmarkIcons[bType]
