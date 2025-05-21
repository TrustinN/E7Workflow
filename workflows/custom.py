from app import E7WorkflowApp, GlobalState, Workflow
from assets import bookmarkIconPaths, bookmarkTypes, penguinIconPaths, penguinTypes
from custom import StatWindow, addStatWindow, makeStatCards
from workflows.nav import buildGrowthAltarWorkflow, buildHomeWorkflow
from workflows.penguin import buildWorkflow as buildPenguinWorkflow
from workflows.shop import buildWorkflow as buildShopWorkflow

WORKFLOW = "Shop Refresh and Resupply"


def buildRefreshAndResupplyWorkflow():
    shopWorkflow = buildShopWorkflow()
    penguinWorkflow = buildPenguinWorkflow()
    homeWorkflow = buildHomeWorkflow()
    growthAltarWorkflow = buildGrowthAltarWorkflow()
    wkflows = [shopWorkflow, penguinWorkflow, homeWorkflow, growthAltarWorkflow]

    def executeTasks(state: GlobalState):
        shopWorkflow.execute(state)
        homeWorkflow.execute(state)

        growthAltarWorkflow.execute(state)
        penguinWorkflow.execute(state)

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
