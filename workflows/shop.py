import time

from app import (
    E7WorkflowApp,
    GlobalState,
    Task,
    Workflow,
    WorkflowState,
    Workspace,
    WorkspaceLayout,
)
from assets import (
    BookmarkType,
    bookmarkIconPaths,
    bookmarkTypes,
    getBookMarkIcon,
    shopItemCnt,
)
from custom import StatWindow, addStatWindow, makeStatCards

from .utils import click, imageMatch, scroll

WORKFLOW = "Shop Refresh"


def updateStats(state: WorkflowState):
    tmp = state.getTemporaryState()
    if tmp["result"]:
        bType = tmp["resultType"]
        stats = state.getWorkflowStats()
        stats[bType.name] += 1


def findBookmark(wkspace: Workflow, state: WorkflowState, **kwargs):
    bmIcon = getBookMarkIcon(kwargs["bmType"])
    imageMatch(wkspace, state, img=bmIcon)
    tmp = state.getTemporaryState()
    if tmp["result"]:
        tmp["resultType"] = kwargs["bmType"]


def findBookmarks(wkspace: Workspace, state: WorkflowState, **kwargs):
    for bmType in kwargs["bmTypes"]:
        findBookmark(wkspace, state, **{"bmType": bmType})
        tmp = state.getTemporaryState()
        if tmp["result"]:
            break


def buildWorkflow():
    # Initialize Workspaces
    iconWS = [Workspace(f"Icon {i + 1}") for i in range(shopItemCnt)]
    buyWS = [Workspace(f"Buy {i + 1}") for i in range(shopItemCnt)]

    entryWS = [
        WorkspaceLayout(f"Entry {i + 1}", [iconWS[i], buyWS[i]])
        for i in range(shopItemCnt)
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

    # Initialize tasks
    findTasks = [Task() for i in range(shopItemCnt)]
    for i in range(shopItemCnt):
        ft = findTasks[i]
        ft.setFunc(
            findBookmarks,
            **{
                "bmTypes": [
                    BookmarkType.MYSTIC,
                    BookmarkType.COVENANT,
                ]
            },
        )
        ft.setWorkspace(iconWS[i])

    buyTasks = [Task() for i in range(shopItemCnt)]
    for i in range(shopItemCnt):
        bt = buyTasks[i]
        bt.setFunc(click)
        bt.setWorkspace(buyWS[i])

    focusTask = Task()
    focusTask.setWorkspace(focusWS)

    scrollTask = Task()
    scrollTask.setWorkspace(scrollWS)
    scrollTask.setFunc(scroll, **{"dir": "up"})

    confirmBuyTask = Task()
    confirmBuyTask.setWorkspace(confirmBuyWS)

    refreshTask = Task()
    refreshTask.setWorkspace(refreshWS)

    confirmRefreshTask = Task()
    confirmRefreshTask.setWorkspace(confirmRefreshWS)

    clickTasks = [focusTask, confirmBuyTask, refreshTask, confirmRefreshTask]
    for c in clickTasks:
        c.setFunc(click)

    def findAndBuy(i: int, state: WorkflowState):
        ft = findTasks[i]
        ct = buyTasks[i]
        ft.execute(state)

        tmp = state.getTemporaryState()
        if tmp["result"] != 0:
            updateStats(state)

            tmp["result"] = 0
            ct.execute(state)
            time.sleep(0.3)
            confirmBuyTask.execute(state)
            time.sleep(0.3)

    def executeTasks(state: GlobalState):
        wkState = state.getWorkflowState(WORKFLOW)
        focusTask.execute(wkState)

        for i in range(shopItemCnt - 2):
            findAndBuy(i, wkState)

        scrollTask.execute(wkState)
        for i in range(shopItemCnt - 2, shopItemCnt):
            findAndBuy(i, wkState)

        refreshTask.execute(wkState)
        time.sleep(0.3)
        confirmRefreshTask.execute(wkState)
        time.sleep(1.2)

    shopWorkflow = Workflow(WORKFLOW, executeTasks, wkspaces)
    return shopWorkflow


def bindToApp(app: E7WorkflowApp, state: GlobalState):
    shopWorkflow = buildWorkflow()
    state.addWorkflowState(shopWorkflow)
    wkState = state.getWorkflowState(WORKFLOW)
    stats = wkState.getWorkflowStats()
    for i in range(len(bookmarkTypes)):
        stats[bookmarkTypes[i].name] = 0

    app.addWorkflow(shopWorkflow, state)

    bmNames = [bm.name for bm in bookmarkTypes]
    shopStatCards = makeStatCards(bmNames, [0] * len(bmNames), bookmarkIconPaths)
    shopStats = StatWindow(shopStatCards)

    addStatWindow(app, shopWorkflow, shopStats)
