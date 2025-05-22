import time

from app import E7WorkflowApp, GlobalState, WorkflowState, Workspace
from assets import (
    BookmarkType,
    bookmarkIconPaths,
    bookmarkTypes,
    getBookMarkIcon,
    shopItemCnt,
)
from custom import STATS, StatWindow, addStatWindow, makeStatCards

from .utils import TaskData, click, imageMatch, scroll

WORKFLOW_NAME = "Shop Refresh"


def findBookmark(wkspace: Workspace, state: WorkflowState, **kwargs):
    bmIcon = getBookMarkIcon(kwargs["bmType"])
    imageMatch(wkspace, state, img=bmIcon)
    if state.getState(TaskData.RESULT):
        state.setState(TaskData.RESULT, kwargs["bmType"])


def findBookmarks(wkspace: Workspace, state: WorkflowState, **kwargs):
    for bmType in kwargs["bmTypes"]:
        findBookmark(wkspace, state, **{"bmType": bmType})
        if state.getState(TaskData.RESULT):
            break


def buildWorkflow():
    # Initialize Workspaces
    iconWS = [Workspace(f"Icon {i + 1}") for i in range(shopItemCnt)]
    buyWS = [Workspace(f"Buy {i + 1}") for i in range(shopItemCnt)]

    entryWS = [
        Workspace(f"Entry {i + 1}", [iconWS[i], buyWS[i]]) for i in range(shopItemCnt)
    ]
    for wks in entryWS:
        wks.setPadding(0)

    focusWS = Workspace("Focus")
    confirmBuyWS = Workspace("Confirm Buy")
    refreshWS = Workspace("Refresh")
    confirmRefreshWS = Workspace("Confirm Refresh")
    scrollWS = Workspace("Scroll")
    extraWS = [focusWS, confirmRefreshWS, confirmBuyWS, refreshWS, scrollWS]

    wkspaces = entryWS
    wkspaces.extend(extraWS)

    def findAndBuy(i: int, state: WorkflowState):
        iWS = iconWS[i]
        bWS = buyWS[i]
        findBookmarks(
            iWS,
            state,
            bmTypes=[
                BookmarkType.MYSTIC,
                BookmarkType.COVENANT,
                BookmarkType.FRIENDSHIP,
            ],
        )

        if state.getState(TaskData.RESULT) != 0:
            bType = state.getState(TaskData.RESULT)
            stats = state.getState(STATS)
            stats[bType] += 1
            state.setState(TaskData.RESULT, 0)

            click(bWS, state)
            time.sleep(0.3)
            click(confirmBuyWS, state)
            time.sleep(0.3)

    def executeTasks(state: GlobalState):
        wkState = state.getWorkflowState(WORKFLOW_NAME)
        click(focusWS, wkState)

        for i in range(shopItemCnt - 2):
            findAndBuy(i, wkState)

        scroll(scrollWS, wkState, dir="up")
        time.sleep(0.3)
        for i in range(shopItemCnt - 2, shopItemCnt):
            findAndBuy(i, wkState)

        click(refreshWS, wkState)
        time.sleep(0.3)
        click(confirmRefreshWS, wkState)
        time.sleep(1.2)

    wkspace = Workspace(WORKFLOW_NAME, wkspaces)
    wkspace.setPadding(15)
    return executeTasks, wkspace


def initState(state: GlobalState):
    state.addWorkflowState(WORKFLOW_NAME)
    wkState = state.getWorkflowState(WORKFLOW_NAME)

    stats = {}
    for i in range(len(bookmarkTypes)):
        stats[bookmarkTypes[i].name] = 0

    wkState.setState(STATS, stats)


def bindToApp(app: E7WorkflowApp, state: GlobalState):
    shopWorkflow, shopWorkspace = buildWorkflow()
    initState(state)

    app.addWorkflow(shopWorkflow, shopWorkspace, state)

    bmNames = [bm.name for bm in bookmarkTypes]
    shopStatCards = makeStatCards(bmNames, [0] * len(bmNames), bookmarkIconPaths)
    shopStats = StatWindow(shopStatCards)

    runner = app.getRunner(WORKFLOW_NAME)
    window = app.getWindow(WORKFLOW_NAME)
    addStatWindow(window, runner, WORKFLOW_NAME, shopStats)
