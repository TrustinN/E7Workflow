import time

from app import E7WorkflowApp, Workspace
from assets import BookmarkType, bookmarkIconPaths, getBookMarkIcon, shopItemCnt
from custom import StatWindow, addStatWindow, makeStatCards
from workflows import Task, TaskData
from workflows.helpers import click, imageMatch, scroll
from workflows.state import (
    CurrencyType,
    GlobalState,
    WorkflowState,
    bookmarkManager,
    currencyManager,
)

WORKFLOW_NAME = "Shop Refresh"
RESULT = TaskData.RESULT
SKYSTONE = CurrencyType.SKYSTONE
GOLD = CurrencyType.GOLD


def findBookmark(wkspace: Workspace, state: WorkflowState, **kwargs):
    bmIcon = getBookMarkIcon(kwargs["bmType"])
    imageMatch(wkspace, state, img=bmIcon)
    if state.getState(RESULT):
        state.setState(RESULT, kwargs["bmType"])


def buildWorkflow():
    # Initialize Workspaces
    iconWS = [Workspace(f"Icon {i + 1}") for i in range(shopItemCnt)]
    buyWS = [Workspace(f"Buy {i + 1}") for i in range(shopItemCnt)]
    pairs = list(zip(iconWS, buyWS))
    entryWS = [Workspace(f"Entry {i + 1}", list(pairs[i])) for i in range(len(pairs))]

    clickWSNames = ["Focus", "Confirm Buy", "Refresh", "Confirm Refresh"]
    clickWS = {name: Workspace(name) for name in clickWSNames}

    scrollWS = Workspace("Scroll")

    wkspaces = []
    wkspaces.extend(entryWS)
    wkspaces.extend(clickWS.values())
    wkspaces.append(scrollWS)

    def executeTasks(state: GlobalState):

        wkState = state.getWorkflowState(WORKFLOW_NAME)

        def findAndBuy(i: int):
            iWS = iconWS[i]
            bWS = buyWS[i]
            buyType = None
            for bmType in BookmarkType:
                findBookmark(iWS, wkState, bmType=bmType)
                if wkState.getState(RESULT):
                    buyType = bmType
                    break

            if buyType:
                click(bWS, wkState)
                time.sleep(0.3)

                click(clickWS["Confirm Buy"], wkState)
                time.sleep(0.3)

                bookmarkManager.addAmount(state, buyType, 1)
                currencyManager.subtractAmount(state, GOLD, buyType.cost)

        click(clickWS["Focus"], wkState)

        for i in range(shopItemCnt - 2):
            findAndBuy(i)

        scroll(scrollWS, wkState, dir="up")
        time.sleep(0.3)
        for i in range(shopItemCnt - 2, shopItemCnt):
            findAndBuy(i)

        click(clickWS["Refresh"], wkState)
        time.sleep(0.3)

        click(clickWS["Confirm Refresh"], wkState)
        time.sleep(1.0)

        currencyManager.subtractAmount(state, SKYSTONE, 3)

    wkspace = Workspace(WORKFLOW_NAME, wkspaces)
    wkspace.setPadding(15)
    return Task(executeTasks), wkspace


def initState(state: GlobalState):
    state.addWorkflowState(WORKFLOW_NAME)


def bindToApp(app: E7WorkflowApp, state: GlobalState):
    shopWorkflow, shopWorkspace = buildWorkflow()
    initState(state)

    app.addWorkflow(shopWorkflow, shopWorkspace, state)

    bmNames = [bm.name for bm in BookmarkType]
    shopStatCards = makeStatCards(bmNames, [0] * len(bmNames), bookmarkIconPaths)
    shopStats = StatWindow(shopStatCards)

    runner = app.getRunner(WORKFLOW_NAME)
    window = app.getWindow(WORKFLOW_NAME)
    addStatWindow(window, runner, bookmarkManager, shopStats)
