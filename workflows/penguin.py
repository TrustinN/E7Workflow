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
from assets import getPenguinIcon, penguinIconPaths, penguinTypes
from custom import StatWindow, addStatWindow, makeStatCards

from .utils import click, filterNumbers, imageMatch, scan

WORKFLOW = "Penguin"

focusTask = Task()
focusWS = Workspace("Focus")

buyTask = Task()
buyWS = Workspace("Buy")

maxTask = Task()
maxWS = Workspace("Max")

confirmTask = Task()
confirmWS = Workspace("Confirm")


def findPenguin(wkspace: Workspace, state: WorkflowState, **kwargs):
    pType = kwargs["pType"]
    pgnIcon = getPenguinIcon(pType)
    imageMatch(
        wkspace,
        state,
        img=pgnIcon,
    )
    tmp = state.getTemporaryState()
    if tmp["result"]:
        tmp["resultType"] = pType


def findPenguins(wkspace: Workspace, state: WorkflowState, **kwargs):
    for pType in penguinTypes:
        findPenguin(wkspace, state, pType=pType)


def getNumber(wkspace: Workspace, state: WorkflowState, **kwargs):
    count = filterNumbers(
        wkspace, state, lBound=[200, 200, 200], uBound=[255, 255, 255]
    )
    state.getTemporaryState()["result"] = count


def updateStats(state: WorkflowState):
    tmp = state.getTemporaryState()
    stats = state.getWorkflowStats()

    pType = tmp["resultType"]
    stats[pType.name] += tmp["result"]


def buildWorkflow():
    penguinScanWS = Workspace("Scan")
    penguinCountWS = Workspace("Count")
    penguinScanAndCountWS = WorkspaceLayout(
        "Scan Start", [penguinScanWS, penguinCountWS]
    )
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

    def scanAndCount(wkspace: Workspace, state: WorkflowState, **kwargs):
        for i in range(len(penguinTypes)):
            penguinScanIcon[i].execute(state)
            tmp = state.getTemporaryState()
            if tmp["result"]:
                penguinScanCount.execute(state)
                updateStats(state)

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

    def executeTasks(state: GlobalState):
        wkState = state.getWorkflowState(WORKFLOW)
        for i in range(len(clickTasks) - 1):
            clickTasks[i].execute(wkState)
            time.sleep(0.2)

        time.sleep(0.2)
        penguinScanAction.execute(wkState)

        exitTask.execute(wkState)
        time.sleep(0.2)

    penguinWorkflow = Workflow(WORKFLOW, executeTasks, wkspaces)
    return penguinWorkflow


def bindToApp(app: E7WorkflowApp, state: GlobalState):
    penguinWorkflow = buildWorkflow()
    state.addWorkflowState(penguinWorkflow)
    wkState = state.getWorkflowState(WORKFLOW)
    stats = wkState.getWorkflowStats()
    for i in range(len(penguinTypes)):
        stats[penguinTypes[i].name] = 0

    app.addWorkflow(penguinWorkflow, state)

    penguinNames = [penguin.name for penguin in penguinTypes]
    penguinStatCards = makeStatCards(
        penguinNames, [0] * len(penguinNames), penguinIconPaths
    )
    penguinStats = StatWindow(penguinStatCards)

    addStatWindow(app, penguinWorkflow, penguinStats)
