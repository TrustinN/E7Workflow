import time

from app import E7WorkflowApp, GlobalState, WorkflowState, Workspace, buildWorkspace
from assets import getPenguinIcon, penguinIconPaths, penguinTypes
from custom import STATS, StatWindow, addStatWindow, makeStatCards

from .utils import TaskData, click, filterNumbers, imageMatch, scan

WORKFLOW_NAME = "Penguin"


def findPenguin(wkspace: Workspace, state: WorkflowState, **kwargs):
    pType = kwargs["pType"]
    pgnIcon = getPenguinIcon(pType)
    imageMatch(
        wkspace,
        state,
        img=pgnIcon,
    )
    if state.getState(TaskData.RESULT):
        state.setState(TaskData.RESULT, pType)
    else:
        state.setState(TaskData.RESULT, None)


def findPenguins(wkspace: Workspace, state: WorkflowState, **kwargs):
    for pType in penguinTypes:
        findPenguin(wkspace, state, pType=pType)
        if state.getState(TaskData.RESULT):
            return


def getNumber(wkspace: Workspace, state: WorkflowState, **kwargs):
    count = filterNumbers(
        wkspace, state, lBound=[200, 200, 200], uBound=[255, 255, 255]
    )
    state.setState(TaskData.RESULT, count)


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

    def scanAndCount(wkspace: Workspace, state: WorkflowState, **kwargs):
        for i in range(len(penguinTypes)):
            findPenguin(penguinScanWS, state, pType=penguinTypes[i])
            if state.getState(TaskData.RESULT):
                stats = state.getState(STATS)

                pType = state.getState(TaskData.RESULT)
                getNumber(penguinCountWS, state)
                count = state.getState(TaskData.RESULT)

                stats[pType] = count

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

        time.sleep(0.2)
        click(clickWkspaces[-1], wkState)
        time.sleep(0.2)

    wkspaces = clickWkspaces
    wkspaces.append(penguinScanPath)

    wkspace = Workspace(WORKFLOW_NAME, wkspaces)
    wkspace.setPadding(15)
    return executeTasks, wkspace


def initState(state: GlobalState):
    state.addWorkflowState(WORKFLOW_NAME)
    wkState = state.getWorkflowState(WORKFLOW_NAME)

    stats = {}
    for i in range(len(penguinTypes)):
        stats[penguinTypes[i].name] = 0

    wkState.setState(STATS, stats)


def bindToApp(app: E7WorkflowApp, state: GlobalState):
    penguinWorkflow, penguinWorkspace = buildWorkflow()
    initState(state)

    app.addWorkflow(penguinWorkflow, penguinWorkspace, state)

    penguinNames = [penguin.name for penguin in penguinTypes]
    penguinStatCards = makeStatCards(
        penguinNames, [0] * len(penguinNames), penguinIconPaths
    )
    penguinStats = StatWindow(penguinStatCards)

    runner = app.getRunner(WORKFLOW_NAME)
    window = app.getWindow(WORKFLOW_NAME)
    addStatWindow(window, runner, WORKFLOW_NAME, penguinStats)
