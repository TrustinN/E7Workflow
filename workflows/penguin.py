import time

from app import E7WorkflowApp, GlobalState, WorkflowState, Workspace
from assets import getPenguinIcon, penguinIconPaths, penguinTypes
from custom import StatWindow, addStatWindow, makeStatCards

from .utils import click, filterNumbers, imageMatch, scan

WORKFLOW_NAME = "Penguin"


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
    penguinScanAndCountWS = Workspace("Scan Start", [penguinScanWS, penguinCountWS])
    penguinScanAndCountWS.setPadding(0)

    penguinScanEndWS = Workspace("Scan End")
    penguinScanPath = Workspace("Scan Path", [penguinScanAndCountWS, penguinScanEndWS])
    penguinScanPath.setPadding(0)

    focusWS = Workspace("Focus")
    buyWS = Workspace("Buy")
    maxWS = Workspace("Max")
    confirmWS = Workspace("Confirm")
    exitWS = Workspace("Exit")
    clickWkspaces = [focusWS, buyWS, maxWS, confirmWS, exitWS]

    def scanAndCount(wkspace: Workspace, state: WorkflowState, **kwargs):
        for i in range(len(penguinTypes)):
            findPenguin(penguinScanWS, state, pType=penguinTypes[i])
            tmp = state.getTemporaryState()
            if tmp["result"]:
                getNumber(penguinCountWS, state)
                updateStats(state)

    def executeTasks(state: GlobalState):
        wkState = state.getWorkflowState(WORKFLOW_NAME)
        for i in range(len(clickWkspaces) - 1):
            click(wkspaces[i], wkState)
            time.sleep(0.2)

        time.sleep(0.2)
        scan(
            penguinScanAndCountWS,
            wkState,
            parent=penguinScanPath,
            count=5,
            dir="horizontal",
            task=scanAndCount,
        )

        click(exitWS, wkState)
        time.sleep(0.2)

    wkspaces = clickWkspaces
    wkspaces.append(penguinScanPath)

    return executeTasks, Workspace(WORKFLOW_NAME, wkspaces)


def bindToApp(app: E7WorkflowApp, state: GlobalState):
    penguinWorkflow, penguinWorkspace = buildWorkflow()
    state.addWorkflowState(penguinWorkspace)
    wkState = state.getWorkflowState(WORKFLOW_NAME)
    stats = wkState.getWorkflowStats()
    for i in range(len(penguinTypes)):
        stats[penguinTypes[i].name] = 0

    app.addWorkflow(penguinWorkflow, penguinWorkspace, state)

    penguinNames = [penguin.name for penguin in penguinTypes]
    penguinStatCards = makeStatCards(
        penguinNames, [0] * len(penguinNames), penguinIconPaths
    )
    penguinStats = StatWindow(penguinStatCards)

    addStatWindow(app, penguinWorkspace, penguinStats)
