from PyQt5.QtWidgets import QSpinBox, QWidget

from app import Workspace
from assets import BookmarkType, getBookMarkIcon
from workflows import Task, TaskData
from workflows.helpers import click, execAndSleep, imageMatch, scroll
from workflows.state import (
    CurrencyType,
    GlobalState,
    WorkflowState,
    bookmarkManager,
    currencyManager,
)
from workflows.widgets import StatWindow, bookmarkCards, updateBookmarkCards

WORKFLOW_NAME = "Shop Refresh"
RESULT = TaskData.RESULT
SKYSTONE = CurrencyType.SKYSTONE
GOLD = CurrencyType.GOLD

ICON_WS_PREFIX = "Icon"
BUY_WS_PREFIX = "Buy"
ENTRY_WS_PREFIX = "Entry"
FOCUS_WS = "Focus"
CONFIRM_BUY_WS = "Confirm Buy"
REFRESH_WS = "Refresh"
CONFIRM_REFRESH_WS = "Confirm Refresh"
SCROLL_WS = "Scroll"

SHOP_ENTRY_CNT = 6


def getIconWSName(i):
    return f"{ICON_WS_PREFIX} {i + 1}"


def getBuyWSName(i):
    return f"{BUY_WS_PREFIX} {i + 1}"


def getEntryWSName(i):
    return f"{ENTRY_WS_PREFIX} {i + 1}"


def findBookmark(wkspace: Workspace, state: WorkflowState, **kwargs) -> bool:
    bmIcon = getBookMarkIcon(kwargs["bmType"])
    imageMatch(wkspace, state, img=bmIcon)
    if state.getState(RESULT):
        return True
    return False


def initState(state: GlobalState):
    state.addWorkflowState(WORKFLOW_NAME)


def initWorkspaces() -> dict[str, Workspace]:

    iconWS = [Workspace(getIconWSName(i)) for i in range(SHOP_ENTRY_CNT)]
    buyWS = [Workspace(getBuyWSName(i)) for i in range(SHOP_ENTRY_CNT)]
    pairs = list(zip(iconWS, buyWS))
    entryWS = [Workspace(getEntryWSName(i), list(pairs[i])) for i in range(len(pairs))]

    clickWSNames = [FOCUS_WS, CONFIRM_BUY_WS, REFRESH_WS, CONFIRM_REFRESH_WS]
    clickWS = {name: Workspace(name) for name in clickWSNames}

    scrollWS = Workspace(SCROLL_WS)

    mainWSChildren = []
    mainWSChildren.extend(entryWS)
    mainWSChildren.extend(clickWS.values())
    mainWSChildren.append(scrollWS)

    workflowWS = Workspace(WORKFLOW_NAME, mainWSChildren)
    workflowWS.setPadding(15)

    # need to make a copy to prevent self-inclusion
    wkspaces = mainWSChildren[:]
    wkspaces.extend(iconWS)
    wkspaces.extend(buyWS)
    wkspaces.append(workflowWS)

    wkspaces = {ws.name: ws for ws in wkspaces}
    return wkspaces


def findAndBuy(i: int, state: GlobalState, wkspaces: dict[str, Workspace]):
    wkState = state.getWorkflowState(WORKFLOW_NAME)

    iWS = wkspaces[getIconWSName(i)]
    bWS = wkspaces[getBuyWSName(i)]
    buyType = next(
        (
            bmType
            for bmType in BookmarkType
            if findBookmark(iWS, wkState, bmType=bmType)
        ),
        None,
    )

    if buyType:
        execAndSleep(click, bWS, wkState)
        execAndSleep(click, wkspaces[CONFIRM_BUY_WS], wkState)

        bookmarkManager.addAmount(buyType, 1)
        currencyManager.subtractAmount(GOLD, buyType.cost)


def initWorkflow(wkspaces: dict[str, Workspace]) -> tuple[Task, Workspace]:

    def executeTasks(state: GlobalState):
        wkState = state.getWorkflowState(WORKFLOW_NAME)

        execAndSleep(click, wkspaces[FOCUS_WS], wkState, sleep=0)
        for i in range(SHOP_ENTRY_CNT - 2):
            findAndBuy(i, state, wkspaces)

        execAndSleep(scroll, wkspaces[SCROLL_WS], wkState, dir="up")
        for i in range(SHOP_ENTRY_CNT - 2, SHOP_ENTRY_CNT):
            findAndBuy(i, state, wkspaces)

        execAndSleep(click, wkspaces[REFRESH_WS], wkState)
        execAndSleep(click, wkspaces[CONFIRM_REFRESH_WS], wkState, sleep=1.0)

        currencyManager.subtractAmount(SKYSTONE, 3)

    return Task(executeTasks)


def initWidgets(task: Task, wkspaces: dict[str, Workspace]) -> list[QWidget]:
    bmStats = StatWindow(bookmarkCards.values())

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

    return [bmStats, goldCountWidget, skystoneCountWidget]
