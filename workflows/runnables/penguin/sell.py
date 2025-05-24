import time

from app import Workspace
from workflows import Task, TaskData
from workflows.helpers import click, filterNumbers
from workflows.state import (
    CurrencyType,
    GlobalState,
    PenguinType,
    WorkflowState,
    currencyManager,
    penguinManager,
)

WORKFLOW_NAME = "Sell Penguin"
RESULT = TaskData.RESULT
GOLD = CurrencyType.GOLD


def getNumber(wkspace: Workspace, state: WorkflowState, **kwargs):
    count = filterNumbers(
        wkspace, state, lBound=[200, 200, 200], uBound=[255, 255, 255]
    )
    state.setState(RESULT, count)


def buildWorkflow():
    clickWSNames = ["Focus", "Sell", "Select", "Confirm"]
    clickWS = {name: Workspace(name) for name in clickWSNames}

    selectWSNames = [pType.name for pType in PenguinType]
    selectWS = {name: Workspace(name) for name in selectWSNames}

    amtWSNames = [f"{pType.name} Amount" for pType in PenguinType]
    amtWS = {name: Workspace(name) for name in amtWSNames}

    scanWSNames = ["Count"]
    scanWS = Workspace(scanWSNames[0])

    wkspaces = []
    wkspaces.extend(clickWS.values())
    wkspaces.extend(selectWS.values())
    wkspaces.extend(amtWS.values())
    wkspaces.append(scanWS)

    delay = 0.2

    def executeTasks(state: GlobalState):

        wkState = state.getWorkflowState(WORKFLOW_NAME)

        def sellPenguin(pType):
            click(selectWS[pType.name], wkState)
            time.sleep(delay)

            click(clickWS["Sell"], wkState)
            time.sleep(delay)

            click(amtWS[f"{pType.name} Amount"], wkState)
            time.sleep(delay)

            click(clickWS["Select"], wkState)
            time.sleep(delay)

            getNumber(scanWS, wkState)
            goldCount = wkState.getState(RESULT)
            time.sleep(delay)

            click(clickWS["Confirm"], wkState)
            time.sleep(delay)

            penguinManager.subtractAmount(state, pType, goldCount // pType.value)
            currencyManager.addAmount(state, GOLD, goldCount)

        click(clickWS["Focus"], wkState)
        time.sleep(delay)

        for pType in PenguinType:
            sellPenguin(pType)

    wkspace = Workspace(WORKFLOW_NAME, wkspaces)
    return Task(executeTasks), wkspace


def initState(state: GlobalState):
    state.addWorkflowState(WORKFLOW_NAME)
