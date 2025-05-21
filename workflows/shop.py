import time

from app import E7WorkflowApp, GlobalState, WorkflowState, Workspace
from assets import (
    BookmarkType,
    bookmarkIconPaths,
    bookmarkTypes,
    getBookMarkIcon,
    shopItemCnt,
)
from custom import StatWindow, addStatWindow, makeStatCards

from .utils import click, imageMatch, scroll

WORKFLOW_NAME = "Shop Refresh"


def updateStats(state: WorkflowState):
    tmp = state.getField("temp")
    if tmp["result"]:
        bType = tmp["resultType"]
        stats = state.getField("stats")
        stats[bType.name] += 1


def findBookmark(wkspace: Workspace, state: WorkflowState, **kwargs):
    bmIcon = getBookMarkIcon(kwargs["bmType"])
    imageMatch(wkspace, state, img=bmIcon)
    tmp = state.getField("temp")
    if tmp["result"]:
        tmp["resultType"] = kwargs["bmType"]


def findBookmarks(wkspace: Workspace, state: WorkflowState, **kwargs):
    for bmType in kwargs["bmTypes"]:
        findBookmark(wkspace, state, **{"bmType": bmType})
        tmp = state.getField("temp")
        if tmp["result"]:
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
            ],
        )

        tmp = state.getField("temp")
        if tmp["result"] != 0:
            updateStats(state)

            tmp["result"] = 0
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


def bindToApp(app: E7WorkflowApp, state: GlobalState):
    shopWorkflow, shopWorkspace = buildWorkflow()
    state.addWorkflowState(shopWorkspace)
    wkState = state.getWorkflowState(WORKFLOW_NAME)
    wkState.addField("stats")
    stats = wkState.getField("stats")
    for i in range(len(bookmarkTypes)):
        stats[bookmarkTypes[i].name] = 0

    app.addWorkflow(shopWorkflow, shopWorkspace, state)

    bmNames = [bm.name for bm in bookmarkTypes]
    shopStatCards = makeStatCards(bmNames, [0] * len(bmNames), bookmarkIconPaths)
    shopStats = StatWindow(shopStatCards)

    runner = app.getRunner(shopWorkspace.name)
    window = app.getWindow(shopWorkspace.name)
    addStatWindow(window, runner, shopWorkspace, shopStats)
