from PyQt5.QtWidgets import QSpinBox, QWidget

import workflows.runnables.penguin.buy as pgnb
import workflows.runnables.penguin.sell as pgns
import workflows.runnables.shop as shop
import workflows.runnables.window as win
from app import Workspace
from workflows import Task
from workflows.helpers import execAndSleep
from workflows.state import (
    ActiveWindow,
    BookmarkType,
    CurrencyType,
    GlobalState,
    currencyManager,
    windowManager,
)
from workflows.widgets import (
    StatWindow,
    bookmarkCards,
    penguinCards,
    updateBookmarkCards,
    updatePenguinCards,
)

WORKFLOW_NAME = "Shop Refresh and Resupply"
SKYSTONE = CurrencyType.SKYSTONE
GOLD = CurrencyType.GOLD

modules = [pgnb, pgns, shop, win]


def initState(state: GlobalState):
    state.addWorkflowState(WORKFLOW_NAME)
    shop.initState(state)
    pgnb.initState(state)
    pgns.initState(state)


def initWorkspaces() -> dict[str, Workspace]:
    pgnBuyWS = pgnb.initWorkspaces()
    pgnSellWS = pgns.initWorkspaces()
    shopWS = shop.initWorkspaces()
    winHomeWS = win.initNavHomeWorkspaces()
    winGrowthAltarWS = win.initNavGrowthAltarWorkspaces()
    winGrowthIngredientsWS = win.initNavGrowthIngredientsWorkspaces()
    winSecretShopWS = win.initNavSecretShopWorkspaces()

    wkspaces = {}
    wkspaces[pgnb.WORKFLOW_NAME] = pgnBuyWS
    wkspaces[pgns.WORKFLOW_NAME] = pgnSellWS
    wkspaces[shop.WORKFLOW_NAME] = shopWS
    wkspaces[win.NAV_HOME_WORKFLOW] = winHomeWS
    wkspaces[win.NAV_GROWTH_ALTAR_WORKFLOW] = winGrowthAltarWS
    wkspaces[win.NAV_GROWTH_INGREDIENTS_WORKFLOW] = winGrowthIngredientsWS
    wkspaces[win.NAV_SECRET_SHOP_WORKFLOW] = winSecretShopWS

    mainWSChildren = [
        pgnBuyWS[pgnb.WORKFLOW_NAME],
        pgnSellWS[pgns.WORKFLOW_NAME],
        shopWS[shop.WORKFLOW_NAME],
        winHomeWS[win.NAV_HOME_WORKFLOW],
        winGrowthAltarWS[win.NAV_GROWTH_ALTAR_WORKFLOW],
        winGrowthIngredientsWS[win.NAV_GROWTH_INGREDIENTS_WORKFLOW],
        winSecretShopWS[win.NAV_SECRET_SHOP_WORKFLOW],
    ]

    workflowWS = Workspace(WORKFLOW_NAME, mainWSChildren)
    workflowWS.setPadding(15)
    wkspaces[WORKFLOW_NAME] = workflowWS

    return wkspaces


def initWorkflow(wkspaces: dict[str, Workspace]) -> Task:
    navSecretShopWorkflow = win.initNavSecretShopWorkflow(
        wkspaces[win.NAV_SECRET_SHOP_WORKFLOW]
    )
    refreshShopWorkflow = shop.initWorkflow(wkspaces[shop.WORKFLOW_NAME])
    buyPenguinWorkflow = pgnb.initWorkflow(wkspaces[pgnb.WORKFLOW_NAME])
    sellPenguinWorkflow = pgns.initWorkflow(wkspaces[pgns.WORKFLOW_NAME])
    navHomeWorkflow = win.initNavHomeWorkflow(wkspaces[win.NAV_HOME_WORKFLOW])
    navGrowthAltarWorkflow = win.initNavGrowthAltarWorkflow(
        wkspaces[win.NAV_GROWTH_ALTAR_WORKFLOW]
    )
    navGrowthIngredientsWorkflow = win.initNavGrowthIngredientsWorkflow(
        wkspaces[win.NAV_GROWTH_INGREDIENTS_WORKFLOW]
    )

    delay = 1.2

    def executeTasks(state: GlobalState):

        numGold = currencyManager.getAmount(GOLD)
        numSkystones = currencyManager.getAmount(SKYSTONE)
        activeWindow = windowManager.getActiveWindow()

        if numGold < BookmarkType.MYSTIC.cost:
            if activeWindow != ActiveWindow.GROWTH_ALTAR:
                execAndSleep(navHomeWorkflow, state, sleep=delay)
                execAndSleep(navGrowthAltarWorkflow, state, sleep=delay)

            execAndSleep(buyPenguinWorkflow, state, sleep=delay)
            execAndSleep(navHomeWorkflow, state, sleep=delay)
            execAndSleep(navGrowthIngredientsWorkflow, state, sleep=delay)
            execAndSleep(sellPenguinWorkflow, state, sleep=delay)

        elif numSkystones >= 3:
            if activeWindow != ActiveWindow.SECRET_SHOP:
                execAndSleep(navHomeWorkflow, state, sleep=delay)
                execAndSleep(navSecretShopWorkflow, state, sleep=delay)

            execAndSleep(refreshShopWorkflow, state, sleep=delay)

    return Task(executeTasks)


def initWidgets(task: Task, wkspaces: dict[str, Workspace]) -> list[QWidget]:
    bmStats = StatWindow()
    bmStats.addCards(bookmarkCards.values())
    bmStats.addCards(penguinCards.values())

    goldCountWidget = QSpinBox()
    goldCountWidget.setMinimum(-1)
    goldCountWidget.setMaximum(1000000000)

    skystoneCountWidget = QSpinBox()
    skystoneCountWidget.setMinimum(-1)
    skystoneCountWidget.setMaximum(1000000000)

    def setManagerCurrencyAmount(currencyType, widget):
        def setter():
            currencyManager.setAmount(currencyType, widget.value())

        return setter

    def setWidgetCurrencyAmount(currencyType, widget):
        def setter(state: GlobalState):
            widget.setValue(currencyManager.getAmount(currencyType))

        return setter

    goldCountWidget.valueChanged.connect(
        setManagerCurrencyAmount(GOLD, goldCountWidget)
    )
    skystoneCountWidget.valueChanged.connect(
        setManagerCurrencyAmount(SKYSTONE, skystoneCountWidget)
    )

    updateGoldWidget = Task(setWidgetCurrencyAmount(GOLD, goldCountWidget))
    updateSkystoneWidget = Task(setWidgetCurrencyAmount(SKYSTONE, skystoneCountWidget))

    task.addTask(updateGoldWidget)
    task.addTask(updateSkystoneWidget)
    task.addTask(updateBookmarkCards)
    task.addTask(updatePenguinCards)

    return [bmStats, goldCountWidget, skystoneCountWidget]
