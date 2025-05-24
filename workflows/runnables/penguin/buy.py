from PyQt5.QtWidgets import QWidget

from app import Workspace
from assets import getPenguinIcon
from workflows import Task, TaskData
from workflows.helpers import click, execAndSleep, filterNumbers, imageMatch, scan
from workflows.state import GlobalState, PenguinType, WorkflowState, penguinManager
from workflows.widgets import StatWindow, penguinCards, updatePenguinCards

SCAN_WS = "Scan"
COUNT_WS = "Count"
SCAN_START_WS = "Scan Start"
SCAN_END_WS = "Scan End"
SCAN_PATH_WS = "Scan Path"

FOCUS_WS = "Focus"
BUY_WS = "Buy"
MAX_WS = "Max"
CONFIRM_WS = "Confirm"
EXIT_WS = "Exit"


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


def initState(state: GlobalState):
    state.addWorkflowState(WORKFLOW_NAME)


def initWorkspaces() -> dict[str, Workspace]:
    penguinScanWS = Workspace(SCAN_WS)
    penguinCountWS = Workspace(COUNT_WS)
    penguinScanAndCountWS = Workspace(SCAN_START_WS, [penguinScanWS, penguinCountWS])

    penguinScanEndWS = Workspace(SCAN_END_WS)
    penguinScanPath = Workspace(SCAN_PATH_WS, [penguinScanAndCountWS, penguinScanEndWS])

    scanWkspaces = [
        penguinScanWS,
        penguinCountWS,
        penguinScanAndCountWS,
        penguinScanEndWS,
        penguinScanPath,
    ]

    clickWSNames = [FOCUS_WS, BUY_WS, MAX_WS, CONFIRM_WS, EXIT_WS]
    clickWkspaces = [Workspace(name) for name in clickWSNames]

    mainWSChildren = clickWkspaces[:]
    mainWSChildren.append(penguinScanPath)
    workflowWS = Workspace(WORKFLOW_NAME, mainWSChildren)
    workflowWS.setPadding(15)

    wkspaces = clickWkspaces[:] + scanWkspaces[:]
    wkspaces.append(workflowWS)

    wkspaces = {ws.name: ws for ws in wkspaces}
    return wkspaces


def initWorkflow(wkspaces: dict[str, Workspace]) -> Task:
    def executeTasks(state: GlobalState):

        def scanAndCount(wkspace: Workspace, wkState: WorkflowState, **kwargs):
            for pType in PenguinType:
                findPenguin(wkspaces[SCAN_WS], wkState, pType=pType)
                if wkState.getState(RESULT):
                    pType = wkState.getState(RESULT)
                    getNumber(wkspaces[COUNT_WS], wkState)
                    count = wkState.getState(RESULT)
                    if count == 0:
                        count = 1

                    penguinManager.addAmount(pType, count)

        wkState = state.getWorkflowState(WORKFLOW_NAME)

        clickOrder = [FOCUS_WS, BUY_WS, MAX_WS, CONFIRM_WS, EXIT_WS]
        for i in range(len(clickOrder) - 1):
            clickWS = clickOrder[i]
            execAndSleep(click, wkspaces[clickWS], wkState)

        execAndSleep(
            scan,
            wkspaces[SCAN_START_WS],
            wkState,
            parent=wkspaces[SCAN_PATH_WS],
            count=5,
            dir="horizontal",
            task=scanAndCount,
        )
        execAndSleep(click, wkspaces[EXIT_WS], wkState)

    return Task(executeTasks)


def initWidgets(task: Task, wkspaces: dict[str, Workspace]) -> list[QWidget]:
    penguinStats = StatWindow(penguinCards.values())
    task.addTask(updatePenguinCards)
    return [penguinStats]
