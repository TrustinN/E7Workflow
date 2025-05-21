import time

from app import E7WorkflowApp, GlobalState, Workflow
from assets import bookmarkIconPaths, bookmarkTypes, penguinIconPaths, penguinTypes
from custom import StatWindow, addStatWindow, makeStatCards
from workflows.nav import buildGrowthAltarWorkflow, buildHomeWorkflow, buildShopWorkflow
from workflows.penguin import buildWorkflow as buildPenguinWorkflow
from workflows.shop import buildWorkflow as buildRefreshShopWorkflow

WORKFLOW = "Shop Refresh and Resupply"


def buildRefreshAndResupplyWorkflow():
    shopWorkflow = buildShopWorkflow()
    refreshShopWorkflow = buildRefreshShopWorkflow()
    penguinWorkflow = buildPenguinWorkflow()
    homeWorkflow = buildHomeWorkflow()
    growthAltarWorkflow = buildGrowthAltarWorkflow()
    wkflows = [
        shopWorkflow,
        refreshShopWorkflow,
        penguinWorkflow,
        homeWorkflow,
        growthAltarWorkflow,
    ]
    delay = 0.4

    def executeTasks(state: GlobalState):
        homeWorkflow.execute(state)
        time.sleep(delay)

        shopWorkflow.execute(state)
        time.sleep(delay)

        refreshShopWorkflow.execute(state)
        time.sleep(delay)
        homeWorkflow.execute(state)
        time.sleep(delay)

        growthAltarWorkflow.execute(state)
        time.sleep(delay)
        penguinWorkflow.execute(state)
        time.sleep(delay)

    refreshAndResupplyWorkflow = Workflow(WORKFLOW, executeTasks, wkspaces=wkflows)
    return refreshAndResupplyWorkflow


def bindToApp(app: E7WorkflowApp, state: GlobalState):
    refreshAndResupplyWorkflow = buildRefreshAndResupplyWorkflow()
    state.addWorkflowState(refreshAndResupplyWorkflow)
    app.addWorkflow(refreshAndResupplyWorkflow, state)

    penguinNames = [penguin.name for penguin in penguinTypes]
    penguinStatCards = makeStatCards(
        penguinNames, [0] * len(penguinNames), penguinIconPaths
    )
    penguinStats = StatWindow(penguinStatCards)

    addStatWindow(app, refreshAndResupplyWorkflow, penguinStats)

    bmNames = [bm.name for bm in bookmarkTypes]
    shopStatCards = makeStatCards(bmNames, [0] * len(bmNames), bookmarkIconPaths)
    shopStats = StatWindow(shopStatCards)

    addStatWindow(app, refreshAndResupplyWorkflow, shopStats)
