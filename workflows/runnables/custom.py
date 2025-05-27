from PyQt5.QtWidgets import QHBoxLayout, QLabel, QSpinBox, QWidget

import workflows.runnables.penguin.buy as pgnb
import workflows.runnables.penguin.sell as pgns
import workflows.runnables.shop as shop
import workflows.runnables.window as win
from app import Workspace
from assets import PenguinType
from workflows import Task
from workflows.helpers import execAndSleep
from workflows.state import (
    ActiveWindow,
    BookmarkType,
    CurrencyType,
    GlobalState,
    currencyManager,
    penguinManager,
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
MIN_GOLD = 3 * BookmarkType.MYSTIC.cost

modules = [pgnb, pgns, shop, win]


def getPenguinsToGold(state: GlobalState) -> int:
    totalGold = 0
    for pType in PenguinType:
        numP = penguinManager.getAmount(pType)
        totalGold += numP * pType.value
    return totalGold


def getMinGoldThreshold():
    return MIN_GOLD


def updateMinGoldThreshold(value: int):
    global MIN_GOLD
    MIN_GOLD = value


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
    winNavBackWS = win.initNavBackWorkspaces()

    wkspaces = {}
    wkspaces[pgnb.WORKFLOW_NAME] = pgnBuyWS
    wkspaces[pgns.WORKFLOW_NAME] = pgnSellWS
    wkspaces[shop.WORKFLOW_NAME] = shopWS
    wkspaces[win.NAV_HOME_WORKFLOW] = winHomeWS
    wkspaces[win.NAV_GROWTH_ALTAR_WORKFLOW] = winGrowthAltarWS
    wkspaces[win.NAV_GROWTH_INGREDIENTS_WORKFLOW] = winGrowthIngredientsWS
    wkspaces[win.NAV_SECRET_SHOP_WORKFLOW] = winSecretShopWS
    wkspaces[win.NAV_BACK_WORKFLOW] = winNavBackWS

    mainWSChildren = [
        pgnBuyWS[pgnb.WORKFLOW_NAME],
        pgnSellWS[pgns.WORKFLOW_NAME],
        shopWS[shop.WORKFLOW_NAME],
        winHomeWS[win.NAV_HOME_WORKFLOW],
        winGrowthAltarWS[win.NAV_GROWTH_ALTAR_WORKFLOW],
        winGrowthIngredientsWS[win.NAV_GROWTH_INGREDIENTS_WORKFLOW],
        winSecretShopWS[win.NAV_SECRET_SHOP_WORKFLOW],
        winNavBackWS[win.NAV_BACK_WORKFLOW],
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
    navBackWorkflow = win.initNavBackWorkflow(wkspaces[win.NAV_BACK_WORKFLOW])

    delay = 1.2

    def executeTasks(state: GlobalState):

        numGold = currencyManager.getAmount(GOLD)
        numSkystones = currencyManager.getAmount(SKYSTONE)
        activeWindow = windowManager.getActiveWindow()

        goldThreshold = getMinGoldThreshold()

        # Buy/Sell penguins
        if numGold < goldThreshold:

            # Sell penguins
            if getPenguinsToGold(state) + numGold >= goldThreshold:
                if activeWindow != ActiveWindow.INVENTORY:
                    execAndSleep(navHomeWorkflow, state, sleep=delay)
                    execAndSleep(navGrowthIngredientsWorkflow, state, sleep=delay)

                execAndSleep(sellPenguinWorkflow, state, sleep=delay)

            # Buy penguins
            else:
                if activeWindow != ActiveWindow.GROWTH_ALTAR:
                    if activeWindow == ActiveWindow.INVENTORY:
                        execAndSleep(navBackWorkflow, state, sleep=delay)
                    else:
                        execAndSleep(navHomeWorkflow, state, sleep=delay)
                    execAndSleep(navGrowthAltarWorkflow, state, sleep=delay)

                execAndSleep(buyPenguinWorkflow, state, sleep=delay)

        # Buy Bookmarks
        elif numSkystones >= 3:
            if activeWindow != ActiveWindow.SECRET_SHOP:
                if activeWindow == ActiveWindow.INVENTORY:
                    execAndSleep(navBackWorkflow, state, sleep=delay)
                else:
                    execAndSleep(navHomeWorkflow, state, sleep=delay)
                execAndSleep(navSecretShopWorkflow, state, sleep=delay)

            execAndSleep(refreshShopWorkflow, state, sleep=delay)

    return Task(executeTasks)


class LabeledSpinBox(QWidget):
    def __init__(self, label):
        super().__init__()
        self.layout = QHBoxLayout()
        self.label = QLabel(label)
        self.input = QSpinBox()
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.input)
        self.setLayout(self.layout)
        self.show()


def initWidgets(task: Task, wkspaces: dict[str, Workspace]) -> list[QWidget]:
    bmStats = StatWindow()
    bmStats.addCards(bookmarkCards.values())
    bmStats.addCards(penguinCards.values())

    goldCountWidget = LabeledSpinBox("Gold: ")
    goldCountWidget.input.setMinimum(-1)
    goldCountWidget.input.setMaximum(1000000000)

    skystoneCountWidget = LabeledSpinBox("Skystone: ")
    skystoneCountWidget.input.setMinimum(-1)
    skystoneCountWidget.input.setMaximum(1000000000)

    def setManagerCurrencyAmount(currencyType, widget):
        def setter():
            currencyManager.setAmount(currencyType, widget.value())

        return setter

    def setWidgetCurrencyAmount(currencyType, widget):
        def setter(state: GlobalState):
            widget.setValue(currencyManager.getAmount(currencyType))

        return setter

    goldCountWidget.input.valueChanged.connect(
        setManagerCurrencyAmount(GOLD, goldCountWidget.input)
    )
    skystoneCountWidget.input.valueChanged.connect(
        setManagerCurrencyAmount(SKYSTONE, skystoneCountWidget.input)
    )

    updateGoldWidget = Task(setWidgetCurrencyAmount(GOLD, goldCountWidget.input))
    updateSkystoneWidget = Task(
        setWidgetCurrencyAmount(SKYSTONE, skystoneCountWidget.input)
    )

    def setGoldThresholdAmount(widget):
        def setter():
            updateMinGoldThreshold(widget.value())

        return setter

    goldThresholdWidget = LabeledSpinBox("Gold Threshold: ")
    goldThresholdWidget.input.valueChanged.connect(
        setGoldThresholdAmount(goldThresholdWidget.input)
    )
    goldThresholdWidget.input.setMinimum(0)
    goldThresholdWidget.input.setMaximum(1000000000)
    goldThresholdWidget.input.setValue(MIN_GOLD)

    task.addTask(updateGoldWidget)
    task.addTask(updateSkystoneWidget)
    task.addTask(updateBookmarkCards)
    task.addTask(updatePenguinCards)

    return [bmStats, goldThresholdWidget, goldCountWidget, skystoneCountWidget]
