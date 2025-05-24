import time

from app import Workspace
from workflows import Task, TaskData
from workflows.helpers import click, execAndSleep, filterNumbers
from workflows.state import (
    CurrencyType,
    GlobalState,
    PenguinType,
    WorkflowState,
    currencyManager,
    penguinManager,
)

FOCUS_WS = "Focus"
SELL_WS = "Sell"
SELECT_WS = "Select"
CONFIRM_WS = "Confirm"
AMOUNT_WS_SUFFIX = "Amount"
COUNT_WS = "Count"

WORKFLOW_NAME = "Sell Penguin"
RESULT = TaskData.RESULT
GOLD = CurrencyType.GOLD


def getNumber(wkspace: Workspace, state: WorkflowState, **kwargs):
    count = filterNumbers(
        wkspace, state, lBound=[200, 200, 200], uBound=[255, 255, 255]
    )
    state.setState(RESULT, count)


def getAmountWSName(pType):
    return f"{pType.name} {AMOUNT_WS_SUFFIX}"


def getSelectPenguinWSName(pType):
    return pType.name


def initState(state: GlobalState):
    state.addWorkflowState(WORKFLOW_NAME)


def initWorkspaces() -> list[str, Workspace]:
    clickWSNames = [FOCUS_WS, SELL_WS, SELECT_WS, CONFIRM_WS]
    clickWS = [Workspace(name) for name in clickWSNames]

    selectPenguinWSNames = [getSelectPenguinWSName(pType) for pType in PenguinType]
    selectWS = [Workspace(name) for name in selectPenguinWSNames]

    amtWSNames = [getAmountWSName(pType) for pType in PenguinType]
    amtWS = [Workspace(name) for name in amtWSNames]

    countWS = Workspace(COUNT_WS)

    mainWSChildren = []
    mainWSChildren.extend(clickWS)
    mainWSChildren.extend(selectWS)
    mainWSChildren.extend(amtWS)
    mainWSChildren.append(countWS)

    workflowWS = Workspace(WORKFLOW_NAME, mainWSChildren)
    workflowWS.setPadding(15)

    wkspaces = mainWSChildren[:]
    wkspaces.append(workflowWS)

    wkspaces = {ws.name: ws for ws in wkspaces}
    return wkspaces


def initWorkflow(wkspaces: dict[str, Workspace]) -> Task:

    def executeTasks(state: GlobalState):

        wkState = state.getWorkflowState(WORKFLOW_NAME)

        def sellPenguin(pType):
            execAndSleep(click, wkspaces[getSelectPenguinWSName(pType)], wkState)
            execAndSleep(click, wkspaces[SELL_WS], wkState)
            execAndSleep(click, wkspaces[getAmountWSName(pType)], wkState)
            execAndSleep(click, wkspaces[SELECT_WS], wkState)
            execAndSleep(getNumber, wkspaces[COUNT_WS], wkState)
            execAndSleep(click, wkspaces[CONFIRM_WS], wkState)

            goldCount = wkState.getState(RESULT)
            penguinManager.subtractAmount(pType, goldCount // pType.value)
            currencyManager.addAmount(GOLD, goldCount)

        execAndSleep(click, wkspaces[FOCUS_WS], wkState)

        for pType in PenguinType:
            sellPenguin(pType)

    return Task(executeTasks)
