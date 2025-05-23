import time

from app import E7WorkflowApp, Workspace
from assets import getPenguinIcon, penguinIconPaths
from custom import StatWindow, addStatWindow, makeStatCards
from workflows import Task, TaskData
from workflows.helpers import click, filterNumbers, imageMatch, scan
from workflows.state import GlobalState, PenguinType, WorkflowState, penguinManager

WORKFLOW_NAME = "Buy Penguin"
RESULT = TaskData.RESULT


def findPenguin(wkspace: Workspace, state: WorkflowState, **kwargs):
    pType = kwargs["pType"]
    pgnIcon = getPenguinIcon(pType)
    imageMatch(
        wkspace,
        state,
        img=pgnIcon,
    )
    if state.getState(RESULT):
        state.setState(RESULT, pType)
    else:
        state.setState(RESULT, None)


def findPenguins(wkspace: Workspace, state: WorkflowState, **kwargs):
    for pType in PenguinType:
        findPenguin(wkspace, state, pType=pType)
        if state.getState(RESULT):
            return


def getNumber(wkspace: Workspace, state: WorkflowState, **kwargs):
    count = filterNumbers(
        wkspace, state, lBound=[200, 200, 200], uBound=[255, 255, 255]
    )
    state.setState(RESULT, count)


def buildWorkflow():
    penguinScanWS = Workspace("Scan")
    penguinCountWS = Workspace("Count")
    penguinScanAndCountWS = Workspace("Scan Start", [penguinScanWS, penguinCountWS])
    penguinScanAndCountWS.setPadding(0)

    penguinScanEndWS = Workspace("Scan End")
    penguinScanPath = Workspace("Scan Path", [penguinScanAndCountWS, penguinScanEndWS])
    penguinScanPath.setPadding(0)

    clickWSNames = ["Focus", "Buy", "Max", "Confirm", "Exit"]
    clickWkspaces = [Workspace(name) for name in clickWSNames]

    def executeTasks(state: GlobalState):
        def scanAndCount(wkspace: Workspace, wkState: WorkflowState, **kwargs):
            for pType in PenguinType:
                findPenguin(penguinScanWS, wkState, pType=pType)
                if wkState.getState(RESULT):
                    pType = wkState.getState(RESULT)
                    getNumber(penguinCountWS, wkState)
                    count = wkState.getState(RESULT)
                    if count == 0:
                        count = 1

                    penguinManager.addAmount(state, pType, count)

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

        time.sleep(0.2)
        click(clickWkspaces[len(clickWkspaces) - 1], wkState)
        time.sleep(0.2)

    wkspaces = clickWkspaces[:]
    wkspaces.append(penguinScanPath)

    wkspace = Workspace(WORKFLOW_NAME, wkspaces)
    wkspace.setPadding(15)
    return Task(executeTasks), wkspace


def initState(state: GlobalState):
    state.addWorkflowState(WORKFLOW_NAME)


def bindToApp(app: E7WorkflowApp, state: GlobalState):
    penguinWorkflow, penguinWorkspace = buildWorkflow()
    initState(state)

    app.addWorkflow(penguinWorkflow, penguinWorkspace, state)

    penguinNames = [penguin.name for penguin in PenguinType]
    penguinStatCards = makeStatCards(
        penguinNames, [0] * len(penguinNames), penguinIconPaths
    )
    penguinStats = StatWindow(penguinStatCards)

    runner = app.getRunner(WORKFLOW_NAME)
    window = app.getWindow(WORKFLOW_NAME)
    addStatWindow(window, runner, penguinManager, penguinStats)
