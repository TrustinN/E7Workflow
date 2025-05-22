import time

from PyQt5.QtWidgets import QSpinBox

from app import E7WorkflowApp, Workspace
from assets import bookmarkIconPaths, penguinIconPaths
from custom import StatWindow, addStatWindow, makeStatCards
from workflows.penguin.buy import buildWorkflow as buildBuyPenguinWorkflow
from workflows.penguin.buy import initState as initBuyPenguinState
from workflows.penguin.sell import buildWorkflow as buildSellPenguinWorkflow
from workflows.penguin.sell import initState as initSellPenguinState
from workflows.shop import buildWorkflow as buildRefreshShopWorkflow
from workflows.shop import initState as initShopState
from workflows.window import (
    buildCurrencyInventoryWorkflow,
    buildGrowthAltarWorkflow,
    buildHomeWorkflow,
    buildShopWorkflow,
)

from .state.inventory.bookmark import BookmarkType, bookmarkManager
from .state.inventory.currency import CurrencyType, currencyManager
from .state.inventory.penguin import PenguinType, penguinManager
from .state.state import GlobalState
from .state.window import ActiveWindow, windowManager

WORKFLOW_NAME = "Shop Refresh and Resupply"
SKYSTONE = CurrencyType.SKYSTONE
GOLD = CurrencyType.GOLD


def buildRefreshAndResupplyWorkflow():
    shopWorkflow, shopWorkspace = buildShopWorkflow()
    refreshShopWorkflow, refreshShopWorkspace = buildRefreshShopWorkflow()
    buyPenguinWorkflow, buyPenguinWorkspace = buildBuyPenguinWorkflow()
    sellPenguinWorkflow, sellPenguinWorkspace = buildSellPenguinWorkflow()
    homeWorkflow, homeWorkspace = buildHomeWorkflow()
    growthAltarWorkflow, growthAltarWorkspace = buildGrowthAltarWorkflow()
    currencyInventoryWorkflow, currencyInventoryWorkspace = (
        buildCurrencyInventoryWorkflow()
    )
    wkspaces = [
        shopWorkspace,
        refreshShopWorkspace,
        buyPenguinWorkspace,
        sellPenguinWorkspace,
        homeWorkspace,
        growthAltarWorkspace,
        currencyInventoryWorkspace,
    ]
    delay = 1.0

    def executeTasks(state: GlobalState):

        numGold = currencyManager.getAmount(state, GOLD)
        numSkystones = currencyManager.getAmount(state, SKYSTONE)
        activeWindow = windowManager.getActiveWindow(state)

        if numGold < BookmarkType.MYSTIC.cost:
            if activeWindow != ActiveWindow.GROWTH_ALTAR:

                homeWorkflow(state)
                time.sleep(delay)

                growthAltarWorkflow(state)
                time.sleep(delay)

            buyPenguinWorkflow(state)
            time.sleep(delay)

            homeWorkflow(state)
            time.sleep(delay)

            currencyInventoryWorkflow(state)
            time.sleep(delay)

            sellPenguinWorkflow(state)
            time.sleep(delay)

        elif numSkystones >= 3:
            if activeWindow != ActiveWindow.SECRET_SHOP:

                homeWorkflow(state)
                time.sleep(delay)

                shopWorkflow(state)
                time.sleep(delay)

            refreshShopWorkflow(state)
            time.sleep(delay)

    wkspace = Workspace(WORKFLOW_NAME, wkspaces)
    wkspace.setPadding(15)
    return executeTasks, wkspace


def initState(state: GlobalState):
    state.addWorkflowState(WORKFLOW_NAME)

    initShopState(state)
    initBuyPenguinState(state)
    initSellPenguinState(state)


def bindToApp(app: E7WorkflowApp, state: GlobalState):
    wkflow, wkspace = buildRefreshAndResupplyWorkflow()

    initState(state)

    app.addWorkflow(wkflow, wkspace, state)
    runner = app.getRunner(WORKFLOW_NAME)
    window = app.getWindow(WORKFLOW_NAME)

    penguinNames = [penguin.name for penguin in PenguinType]
    penguinStatCards = makeStatCards(
        penguinNames, [0] * len(penguinNames), penguinIconPaths
    )
    penguinStats = StatWindow(penguinStatCards)

    addStatWindow(window, runner, penguinManager, penguinStats)

    bmNames = [bm.name for bm in BookmarkType]
    shopStatCards = makeStatCards(bmNames, [0] * len(bmNames), bookmarkIconPaths)
    shopStats = StatWindow(shopStatCards)

    addStatWindow(window, runner, bookmarkManager, shopStats)

    goldCountWidget = QSpinBox()
    goldCountWidget.setMinimum(-1)

    skystoneCountWidget = QSpinBox()
    skystoneCountWidget.setMinimum(-1)

    def setCurrencyAmount(currencyType):
        def setter(value):
            currencyManager.setAmount(state, currencyType, value)

        return setter

    goldCountWidget.valueChanged.connect(setCurrencyAmount(GOLD))
    skystoneCountWidget.valueChanged.connect(setCurrencyAmount(SKYSTONE))
    goldCountWidget.setMaximum(1000000000)
    skystoneCountWidget.setMaximum(1000000000)

    window.addWidget(goldCountWidget)
    window.addWidget(skystoneCountWidget)
