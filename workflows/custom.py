import time

from PyQt5.QtWidgets import QSpinBox

from app import E7WorkflowApp, GlobalState, Workspace
from assets import (
    ActiveWindow,
    BookmarkType,
    CurrencyType,
    bookmarkIconPaths,
    bookmarkTypes,
    getBookmarkType,
    getPenguinType,
    penguinIconPaths,
    penguinTypes,
)
from custom import STATS, StatWindow, addStatWindow, makeStatCards
from workflows.nav import (
    ACTIVE_WINDOW,
    buildGrowthAltarWorkflow,
    buildHomeWorkflow,
    buildShopWorkflow,
)
from workflows.penguin import WORKFLOW_NAME as PENGUIN_WORKFLOW_NAME
from workflows.penguin import buildWorkflow as buildPenguinWorkflow
from workflows.penguin import initState as initPenguinState
from workflows.shop import WORKFLOW_NAME as BOOKMARK_WORKFLOW_NAME
from workflows.shop import buildWorkflow as buildRefreshShopWorkflow
from workflows.shop import initState as initShopState

WORKFLOW_NAME = "Shop Refresh and Resupply"
SKYSTONE = CurrencyType.SKYSTONE
GOLD = CurrencyType.GOLD
CURRENCY = "Currency"


def buildRefreshAndResupplyWorkflow():
    shopWorkflow, shopWorkspace = buildShopWorkflow()
    refreshShopWorkflow, refreshShopWorkspace = buildRefreshShopWorkflow()
    penguinWorkflow, penguinWorkspace = buildPenguinWorkflow()
    homeWorkflow, homeWorkspace = buildHomeWorkflow()
    growthAltarWorkflow, growthAltarWorkspace = buildGrowthAltarWorkflow()
    wkspaces = [
        shopWorkspace,
        refreshShopWorkspace,
        penguinWorkspace,
        homeWorkspace,
        growthAltarWorkspace,
    ]
    delay = 1.5

    def executeTasks(state: GlobalState):
        wkState = state.getWorkflowState(WORKFLOW_NAME)

        cState = wkState.getState(CURRENCY)
        if cState[SKYSTONE] != -1 and cState[SKYSTONE] <= 3:
            return

        if cState[SKYSTONE] != -1:
            cState[SKYSTONE] -= 3

        if cState[GOLD] < BookmarkType.MYSTIC.cost:
            if wkState[ACTIVE_WINDOW] != ActiveWindow.GROWTH_ALTAR:

                homeWorkflow(state)
                time.sleep(delay)

                growthAltarWorkflow(state)
                time.sleep(delay)

            penguinWorkflow(state)
            time.sleep(delay)

            newPenguins = {}
            penguinState = state.getWorkflowState(PENGUIN_WORKFLOW_NAME)
            curStats = penguinState.getState(STATS)
            if "prevPenguinStats" in wkState:
                prevPenguinStats = wkState["prevPenguinStats"]
                for penguinName in prevPenguinStats:
                    newPenguins[penguinName] = (
                        curStats[penguinName] - prevPenguinStats[penguinName]
                    )

            else:
                newPenguins = curStats

            wkState["prevPenguinStats"] = curStats
            for penguinName in newPenguins:
                count = newPenguins[penguinName]
                pType = getPenguinType(penguinName)
                cState[GOLD] += count * pType.value

        else:
            if wkState[ACTIVE_WINDOW] != ActiveWindow.SHOP:

                homeWorkflow(state)
                time.sleep(delay)

                shopWorkflow(state)
                time.sleep(delay)

            refreshShopWorkflow(state)
            time.sleep(delay)

            newBookmarks = {}
            bookmarkState = state.getWorkflowState(BOOKMARK_WORKFLOW_NAME)
            curStats = bookmarkState.getState(STATS)
            if "prevBookmarkStats" in wkState:
                prevBookmarkStats = wkState["prevBookmarkStats"]
                for bmName in prevBookmarkStats:
                    newBookmarks[bmName] = curStats[bmName] - prevBookmarkStats[bmName]

            else:
                newBookmarks = curStats

            wkState["prevBookmarkStats"] = curStats
            print(newBookmarks)
            for bmName in newBookmarks:
                count = newBookmarks[bmName]
                bType = getBookmarkType(bmName)
                cState[GOLD] -= count * bType.cost

        print(cState[GOLD])

    wkspace = Workspace(WORKFLOW_NAME, wkspaces)
    wkspace.setPadding(15)
    return executeTasks, wkspace


def initState(state: GlobalState):
    state.addWorkflowState(WORKFLOW_NAME)
    wkState = state.getWorkflowState(WORKFLOW_NAME)
    wkState[ACTIVE_WINDOW] = ActiveWindow.SHOP
    wkState.setState(CURRENCY, {})
    cState = wkState.getState(CURRENCY)
    cState[GOLD] = -1
    cState[SKYSTONE] = -1

    initShopState(state)
    initPenguinState(state)


def bindToApp(app: E7WorkflowApp, state: GlobalState):
    wkflow, wkspace = buildRefreshAndResupplyWorkflow()

    initState(state)

    app.addWorkflow(wkflow, wkspace, state)
    runner = app.getRunner(WORKFLOW_NAME)
    window = app.getWindow(WORKFLOW_NAME)

    penguinNames = [penguin.name for penguin in penguinTypes]
    penguinStatCards = makeStatCards(
        penguinNames, [0] * len(penguinNames), penguinIconPaths
    )
    penguinStats = StatWindow(penguinStatCards)

    addStatWindow(window, runner, PENGUIN_WORKFLOW_NAME, penguinStats)

    bmNames = [bm.name for bm in bookmarkTypes]
    shopStatCards = makeStatCards(bmNames, [0] * len(bmNames), bookmarkIconPaths)
    shopStats = StatWindow(shopStatCards)

    addStatWindow(window, runner, BOOKMARK_WORKFLOW_NAME, shopStats)

    goldCountWidget = QSpinBox()
    goldCountWidget.setMinimum(-1)

    skystoneCountWidget = QSpinBox()
    skystoneCountWidget.setMinimum(-1)

    wkState = state.getWorkflowState(WORKFLOW_NAME)
    cState = wkState.getState(CURRENCY)

    def setGoldAmount(value):
        cState[GOLD] = value

    def setSkystoneAmount(value):
        cState[SKYSTONE] = value

    goldCountWidget.valueChanged.connect(setGoldAmount)
    skystoneCountWidget.valueChanged.connect(setSkystoneAmount)
    goldCountWidget.setMaximum(1000000000)
    skystoneCountWidget.setMaximum(1000000000)

    window.addWidget(goldCountWidget)
    window.addWidget(skystoneCountWidget)
