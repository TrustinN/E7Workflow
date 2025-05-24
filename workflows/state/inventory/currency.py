from assets import CurrencyType

from .manager import InventoryManager

SCOPE = "Currency Scope"


currencyManager = InventoryManager(SCOPE, CurrencyType)
