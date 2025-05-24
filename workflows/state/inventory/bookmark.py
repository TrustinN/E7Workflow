from assets import BookmarkType

from .manager import InventoryManager

SCOPE = "Bookmark Scope"


bookmarkManager = InventoryManager(SCOPE, BookmarkType)
