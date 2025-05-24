from app import Workspace
from workflows import Task
from workflows.helpers import click, execAndSleep
from workflows.state import ActiveWindow, GlobalState, windowManager

FOCUS_WS = "Focus"
MENU_WS = "Menu"
HOME_WS = "Home"
SANCTUARY_WS = "Sanctuary"
FOREST_OF_SOULS_WS = "Forest of Souls"
GROWTH_ALTAR_WS = "Growth Altar"
SECRET_SHOP_WS = "Secret Shop"
INVENTORY_WS = "Inventory"
ITEMS_WS = "Items"
GROWTH_INGREDIENTS_WS = "Growth Ingredients"


NAV_HOME_WORKFLOW = "Nav Home"
NAV_GROWTH_ALTAR_WORKFLOW = "Nav Growth Altar"
NAV_SECRET_SHOP_WORKFLOW = "Nav Secret Shop"
NAV_GROWTH_INGREDIENTS_WORKFLOW = "Nav Growth Ingredients"


def initNavHomeWorkspaces() -> dict[str, Workspace]:

    wsNames = [FOCUS_WS, MENU_WS, HOME_WS]
    mainWSChildren = [Workspace(n) for n in wsNames]
    workflowWS = Workspace(NAV_HOME_WORKFLOW, mainWSChildren)
    workflowWS.setPadding(15)

    wkspaces = mainWSChildren[:]
    wkspaces.append(workflowWS)

    wkspaces = {ws.name: ws for ws in wkspaces}
    return wkspaces


def initNavHomeWorkflow(wkspaces: dict[str, Workspace]):

    def executeTasks(state: GlobalState):
        clickOrder = [FOCUS_WS, MENU_WS, HOME_WS]

        for c in clickOrder:
            execAndSleep(click, wkspaces[c], state)

        windowManager.setActiveWindow(ActiveWindow.HOME)

    return Task(executeTasks)


def initNavGrowthAltarWorkspaces() -> dict[str, Workspace]:
    wsNames = [FOCUS_WS, SANCTUARY_WS, FOREST_OF_SOULS_WS, GROWTH_ALTAR_WS]
    mainWSChildren = [Workspace(n) for n in wsNames]
    workflowWS = Workspace(NAV_GROWTH_ALTAR_WORKFLOW, mainWSChildren)
    workflowWS.setPadding(15)

    wkspaces = mainWSChildren[:]
    wkspaces.append(workflowWS)

    wkspaces = {ws.name: ws for ws in wkspaces}
    return wkspaces


def initNavGrowthAltarWorkflow(wkspaces: dict[str, Workspace]):

    delays = [0.2, 3.0, 0.5, 0.5]

    def executeTasks(state: GlobalState):

        clickOrder = [FOCUS_WS, SANCTUARY_WS, FOREST_OF_SOULS_WS, GROWTH_ALTAR_WS]
        for i in range(len(clickOrder)):
            wsName = clickOrder[i]
            execAndSleep(click, wkspaces[wsName], state, sleep=delays[i])

        windowManager.setActiveWindow(ActiveWindow.GROWTH_ALTAR)

    return Task(executeTasks)


def initNavSecretShopWorkspaces() -> dict[str, Workspace]:
    wsNames = [FOCUS_WS, SECRET_SHOP_WS]
    mainWSChildren = [Workspace(n) for n in wsNames]
    workflowWS = Workspace(NAV_SECRET_SHOP_WORKFLOW, mainWSChildren)
    workflowWS.setPadding(15)

    wkspaces = mainWSChildren[:]
    wkspaces.append(workflowWS)

    wkspaces = {ws.name: ws for ws in wkspaces}
    return wkspaces


def initNavSecretShopWorkflow(wkspaces: dict[str, Workspace]):

    def executeTasks(state: GlobalState):

        clickOrder = [FOCUS_WS, SECRET_SHOP_WS]
        for c in clickOrder:
            execAndSleep(click, wkspaces[c], state)

        windowManager.setActiveWindow(ActiveWindow.SECRET_SHOP)

    return Task(executeTasks)


def initNavGrowthIngredientsWorkspaces() -> dict[str, Workspace]:

    wsNames = [FOCUS_WS, INVENTORY_WS, ITEMS_WS, GROWTH_INGREDIENTS_WS]
    mainWSChildren = [Workspace(n) for n in wsNames]
    workflowWS = Workspace(NAV_GROWTH_INGREDIENTS_WORKFLOW, mainWSChildren)
    workflowWS.setPadding(15)

    wkspaces = mainWSChildren[:]
    wkspaces.append(workflowWS)

    wkspaces = {ws.name: ws for ws in wkspaces}
    return wkspaces


def initNavGrowthIngredientsWorkflow(wkspaces: dict[str, Workspace]):

    def executeTasks(state: GlobalState):

        clickOrder = [FOCUS_WS, INVENTORY_WS, ITEMS_WS, GROWTH_INGREDIENTS_WS]

        for c in clickOrder:
            execAndSleep(click, wkspaces[c], state)

        windowManager.setActiveWindow(ActiveWindow.INVENTORY)

    return Task(executeTasks)
