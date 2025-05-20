import time

from app import Task, Workflow, Workspace, WorkspaceLayout
from assets import BookmarkType, bookmarkTypes, getBookMarkIcon, shopItemCnt

from .utils import click, imageMatch, scroll


def updateStats(state):

    if "bmStats" not in state:
        state["bmStats"] = dict(zip(bookmarkTypes, [0] * len(bookmarkTypes)))

    if state["temp"]["result"]:
        bType = state["temp"]["resultType"]
        state["bmStats"][bType] += 1

    return state


def findBookmark(wkspace, state, **kwargs):
    bmIcon = getBookMarkIcon(kwargs["bmType"])
    state = imageMatch(wkspace, state, bmIcon)
    if state["temp"]["result"]:
        state["temp"]["resultType"] = kwargs["bmType"]

    return state


def findBookmarks(wkspace, state, **kwargs):
    for bmType in kwargs["bmTypes"]:
        state = findBookmark(wkspace, state, **{"bmType": bmType})
        if state["temp"]["result"]:
            break
    return state


# Initialize Workspaces
iconWS = [Workspace(f"Icon {i + 1}") for i in range(shopItemCnt)]
buyWS = [Workspace(f"Buy {i + 1}") for i in range(shopItemCnt)]

entryWS = [
    WorkspaceLayout(f"Entry {i + 1}", [iconWS[i], buyWS[i]]) for i in range(shopItemCnt)
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


def findAndBuy(i, state):
    ft = findTasks[i]
    ct = buyTasks[i]
    state = ft.execute(state)

    if state["temp"]["result"] != 0:
        state = updateStats(state)

        state["temp"]["result"] = 0
        state = ct.execute(state)
        time.sleep(0.3)
        state = confirmBuyTask.execute(state)
        time.sleep(0.3)

    return state


def executeTasks(state):
    state["temp"] = {"result": 0}
    state = focusTask.execute(state)

    for i in range(shopItemCnt - 2):
        state = findAndBuy(i, state)

    state = scrollTask.execute(state)
    for i in range(shopItemCnt - 2, shopItemCnt):
        state = findAndBuy(i, state)

    state = refreshTask.execute(state)
    time.sleep(0.3)
    state = confirmRefreshTask.execute(state)
    time.sleep(1.2)

    return state


shopWorkflow = Workflow("Shop Refresh", executeTasks, wkspaces)
