import time

from app import E7WorkflowApp, GlobalState, Workspace
from assets import (
    BookmarkType,
    PenguinTypes,
    bookmarkIconPaths,
    bookmarkTypes,
    penguinIconPaths,
    penguinTypes,
)
from custom import StatWindow, addStatWindow, makeStatCards
from workflows.nav import buildGrowthAltarWorkflow, buildHomeWorkflow, buildShopWorkflow
from workflows.penguin import WORKFLOW_NAME as PENGUIN_WORKFLOW_NAME
from workflows.penguin import buildWorkflow as buildPenguinWorkflow
from workflows.shop import WORKFLOW_NAME as BOOKMARK_WORKFLOW_NAME
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
    delay = 1.5

    def executeTasks(state: GlobalState):
        wkState = state.getWorkflowState(WORKFLOW_NAME)

        cState = wkState.getField("currency")
        if cState["Skystone"] < 3:
            return

        if cState["Gold"] < BookmarkType.MYSTIC.cost:
            if wkState["winActive"] != "GrowthAltar":

                homeWorkflow(state)
                wkState["winActive"] = "Home"
                time.sleep(delay)

                growthAltarWorkflow(state)
                wkState["winActive"] = "GrowthAltar"
                time.sleep(delay)

            penguinWorkflow(state)
            time.sleep(delay)

            newPenguins = {}
            penguinState = state.getWorkflowState(PENGUIN_WORKFLOW_NAME)
            curStats = penguinState.getField("stats")
            if "prevPenguinStats" in wkState:
                prevPenguinStats = wkState["prevPenguinStats"]
                for penguinName in prevPenguinStats:
                    newPenguins[penguinName] = (
                        curStats[penguinName] - prevPenguinStats[penguinName]
                    )

            else:
                newPenguins = curStats

            wkState["prevPenguinStats"] = curStats
            for penguinName in newPenguins:
                count = newPenguins[penguinName]
                print(penguinName, count)
                if penguinName == PenguinTypes.EPIC.name:
                    cState["Gold"] += count * PenguinTypes.EPIC.value

                elif penguinName == PenguinTypes.EXPERIENCED.name:
                    cState["Gold"] += count * PenguinTypes.EXPERIENCED.value

                elif penguinName == PenguinTypes.NEWBIE.name:
                    cState["Gold"] += count * PenguinTypes.NEWBIE.value

        else:
            if wkState["winActive"] != "Shop":

                homeWorkflow(state)
                wkState["winActive"] = "Home"
                time.sleep(delay)

                shopWorkflow(state)
                wkState["winActive"] = "Shop"
                time.sleep(delay)

            refreshShopWorkflow(state)
            time.sleep(delay)

            newBookmarks = {}
            bookmarkState = state.getWorkflowState(BOOKMARK_WORKFLOW_NAME)
            curStats = bookmarkState.getField("stats")
            if "prevBookmarkStats" in wkState:
                prevBookmarkStats = wkState["prevBookmarkStats"]
                for bmName in prevBookmarkStats:
                    newBookmarks[bmName] = curStats[bmName] - prevBookmarkStats[bmName]

            else:
                newBookmarks = curStats

            wkState["prevBookmarkStats"] = curStats
            for bmName in newBookmarks:
                count = newBookmarks[bmName]
                if bmName == BookmarkType.MYSTIC.name:
                    cState["Gold"] -= count * BookmarkType.MYSTIC.cost

                elif bmName == BookmarkType.COVENANT.name:
                    cState["Gold"] -= count * BookmarkType.MYSTIC.cost

                elif bmName == BookmarkType.FRIENDSHIP.name:
                    cState["Gold"] -= count * BookmarkType.FRIENDSHIP.cost

    wkspace = Workspace(WORKFLOW_NAME, wkspaces)
    wkspace.setPadding(15)
    return executeTasks, wkspace


def bindToApp(app: E7WorkflowApp, state: GlobalState):
    wkflow, wkspace = buildRefreshAndResupplyWorkflow()
    state.addWorkflowState(wkspace)
    wkState = state.getWorkflowState(WORKFLOW_NAME)
    wkState.addField("stats")

    wkFlowWkspaces = {}
    for wks in wkspace.wkspaces:
        wkFlowWkspaces[wks.name] = wks

    wkState["winActive"] = "Shop"
    wkState.addField("currency")
    cState = wkState.getField("currency")
    cState["Gold"] = BookmarkType.COVENANT.cost
    cState["Skystone"] = 10

    app.addWorkflow(wkflow, wkspace, state)
    runner = app.getRunner(wkspace.name)
    window = app.getWindow(wkspace.name)

    penguinNames = [penguin.name for penguin in penguinTypes]
    penguinStatCards = makeStatCards(
        penguinNames, [0] * len(penguinNames), penguinIconPaths
    )
    penguinStats = StatWindow(penguinStatCards)

    penguinWorkspace = wkFlowWkspaces[PENGUIN_WORKFLOW_NAME]
    addStatWindow(window, runner, penguinWorkspace, penguinStats)

    bmNames = [bm.name for bm in bookmarkTypes]
    shopStatCards = makeStatCards(bmNames, [0] * len(bmNames), bookmarkIconPaths)
    shopStats = StatWindow(shopStatCards)

    bookmarkWorkspace = wkFlowWkspaces[BOOKMARK_WORKFLOW_NAME]
    addStatWindow(window, runner, bookmarkWorkspace, shopStats)
