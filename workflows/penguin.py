import time

from app import Task, Workflow, Workspace, WorkspaceLayout
from assets import getPenguinIcon, penguinTypes

from .utils import click, filterNumbers, imageMatch, scan

focusTask = Task()
focusWS = Workspace("Focus")

buyTask = Task()
buyWS = Workspace("Buy")

maxTask = Task()
maxWS = Workspace("Max")

confirmTask = Task()
confirmWS = Workspace("Confirm")


def findPenguin(wkspace, state, **kwargs):
    pType = kwargs["pType"]
    pgnIcon = getPenguinIcon(pType)
    state = imageMatch(
        wkspace,
        state,
        img=pgnIcon,
    )
    if state["temp"]["result"]:
        state["temp"]["resultType"] = pType
    return state


def findPenguins(wkspace, state, **kwargs):
    for pType in penguinTypes:
        state = findPenguin(wkspace, state, pType=pType)
    return state


def getNumber(wkspace, state, **kwargs):
    count = filterNumbers(
        wkspace, state, lBound=[200, 200, 200], uBound=[255, 255, 255]
    )
    state["temp"]["result"] = count
    return state


def updateStats(state):
    if "penguinStats" not in state:
        state["penguinStats"] = dict(zip(penguinTypes, [0] * len(penguinTypes)))

    pType = state["temp"]["resultType"]
    state["penguinStats"][pType] += state["temp"]["result"]

    return state


penguinScanWS = Workspace("Scan")
penguinCountWS = Workspace("Count")
penguinScanAndCountWS = WorkspaceLayout("Scan Start", [penguinScanWS, penguinCountWS])
penguinScanAndCountWS.setPadding(0)

penguinScanEndWS = Workspace("Scan End")
penguinScanPath = WorkspaceLayout(
    "Scan Path", [penguinScanAndCountWS, penguinScanEndWS]
)
penguinScanPath.setPadding(0)

penguinScanAction = Task()
penguinScanAction.setWorkspace(penguinScanAndCountWS)
penguinScanIcon = [Task() for i in range(len(penguinTypes))]
penguinScanCount = Task()
penguinScanCount.setFunc(getNumber)
penguinScanCount.setWorkspace(penguinCountWS)

for i in range(len(penguinTypes)):
    penguinScanIcon[i].setWorkspace(penguinScanWS)
    penguinScanIcon[i].setFunc(findPenguin, pType=penguinTypes[i])

penguinScanAndCount = Task()


def scanAndCount(wkspace, state, **kwargs):
    for i in range(len(penguinTypes)):
        state = penguinScanIcon[i].execute(state)
        if state["temp"]["result"]:
            state = penguinScanCount.execute(state)
            state = updateStats(state)
    return state


penguinScanAndCount.setFunc(scanAndCount)


for i in range(len(penguinTypes)):
    penguinScanAction.setFunc(
        scan,
        parent=penguinScanPath,
        count=5,
        dir="horizontal",
        task=penguinScanAndCount,
    )

exitTask = Task()
exitWS = Workspace("Exit")

clickTasks = [focusTask, buyTask, maxTask, confirmTask, exitTask]
wkspaces = [focusWS, buyWS, maxWS, confirmWS, exitWS, penguinScanPath]


for i in range(len(clickTasks)):
    clickTasks[i].setWorkspace(wkspaces[i])
    clickTasks[i].setFunc(click)


def executeTasks(state):
    state["temp"] = {}
    for i in range(len(clickTasks) - 1):
        state = clickTasks[i].execute(state)
        time.sleep(0.2)

    time.sleep(0.2)
    state = penguinScanAction.execute(state)

    time.sleep(0.4)
    exitTask.execute(state)
    time.sleep(0.2)

    return state


penguinWorkflow = Workflow("Penguin", executeTasks, wkspaces)
