from enum import Enum

from .manager import InventoryManager

SCOPE = "Currency Scope"


class CurrencyType(Enum):
    GOLD = "Gold"
    SKYSTONE = "Skystone"


currencyManager = InventoryManager(SCOPE, CurrencyType)
