import time

from app import E7WorkflowApp, GlobalState, Workspace
from assets import bookmarkIconPaths, bookmarkTypes, penguinIconPaths, penguinTypes
from custom import StatWindow, addStatWindow, makeStatCards
from workflows.nav import buildGrowthAltarWorkflow, buildHomeWorkflow, buildShopWorkflow
from workflows.penguin import buildWorkflow as buildPenguinWorkflow
from workflows.shop import buildWorkflow as buildRefreshShopWorkflow

WORKFLOW_NAME = "Shop Refresh and Resupply"


def buildRefreshAndResupplyWorkflow():
    shopWorkflow, shopWorkspace = buildShopWorkflow()
    refreshShopWorkflow, refreshShopWorkspace = buildRefreshShopWorkflow()
    penguinWorkflow, penguinWorkspace = buildPenguinWorkflow()
    homeWorkflow, homeWorkspace = buildHomeWorkflow()
    growthAltarWorkflow, growthAltarWorkspace = buildGrowthAltarWorkflow()
    wkspaces = [
        shopWorkspace,
        refreshShopWorkspace,
        penguinWorkspace,
        homeWorkspace,
        growthAltarWorkspace,
    ]
    delay = 0.4

    def executeTasks(state: GlobalState):
        homeWorkflow(state)
        time.sleep(delay)

        shopWorkflow(state)
        time.sleep(delay)

        refreshShopWorkflow(state)
        time.sleep(delay)
        homeWorkflow(state)
        time.sleep(delay)

        growthAltarWorkflow(state)
        time.sleep(delay)
        penguinWorkflow(state)
        time.sleep(delay)

    wkspace = Workspace(WORKFLOW_NAME, wkspaces)
    wkspace.setPadding(15)
    return executeTasks, wkspace


def bindToApp(app: E7WorkflowApp, state: GlobalState):
    wkflow, wkspace = buildRefreshAndResupplyWorkflow()
    state.addWorkflowState(wkspace)
    app.addWorkflow(wkflow, wkspace, state)

    penguinNames = [penguin.name for penguin in penguinTypes]
    penguinStatCards = makeStatCards(
        penguinNames, [0] * len(penguinNames), penguinIconPaths
    )
    penguinStats = StatWindow(penguinStatCards)

    addStatWindow(app, wkspace, penguinStats)

    bmNames = [bm.name for bm in bookmarkTypes]
    shopStatCards = makeStatCards(bmNames, [0] * len(bmNames), bookmarkIconPaths)
    shopStats = StatWindow(shopStatCards)

    addStatWindow(app, wkspace, shopStats)
