import time

from app import Workspace

from .state.state import GlobalState
from .state.window import ActiveWindow, windowManager
from .utils import click


def buildHomeWorkflow():

    wsNames = ["Focus", "Menu", "Home"]
    wkspaces = [Workspace(n) for n in wsNames]
    delays = [0.2] * len(wsNames)

    def executeTasks(state: GlobalState):
        for i in range(len(wkspaces)):
            click(wkspaces[i], state)
            time.sleep(delays[i])
        windowManager.setActiveWindow(state, ActiveWindow.HOME)

    wkspace = Workspace("Go Home", wkspaces)
    wkspace.setPadding(15)
    return executeTasks, wkspace


def buildGrowthAltarWorkflow():

    wsNames = ["Focus", "Sanctuary", "Forest of Souls", "Growth Altar"]
    wkspaces = [Workspace(n) for n in wsNames]
    delays = [0.2, 3.0, 0.5, 0.5]

    def executeTasks(state: GlobalState):
        for i in range(len(wkspaces)):
            click(wkspaces[i], state)
            time.sleep(delays[i])
        windowManager.setActiveWindow(state, ActiveWindow.GROWTH_ALTAR)

    wkspace = Workspace("Go Growth Altar", wkspaces)
    wkspace.setPadding(15)
    return executeTasks, wkspace


def buildShopWorkflow():
    wsNames = ["Focus", "Shop"]
    wkspaces = [Workspace(n) for n in wsNames]
    delays = [0.2] * len(wkspaces)

    def executeTasks(state: GlobalState):
        for i in range(len(wkspaces)):
            click(wkspaces[i], state)
            time.sleep(delays[i])
        windowManager.setActiveWindow(state, ActiveWindow.SECRET_SHOP)

    wkspace = Workspace("Go Shop", wkspaces)
    wkspace.setPadding(15)
    return executeTasks, wkspace


def buildCurrencyInventoryWorkflow():
    wsNames = ["Focus", "Inventory", "Currency", "Growth"]
    wkspaces = [Workspace(n) for n in wsNames]
    delays = [0.2] * len(wkspaces)

    def executeTasks(state: GlobalState):
        for i in range(len(wkspaces)):
            click(wkspaces[i], state)
            time.sleep(delays[i])

        windowManager.setActiveWindow(state, ActiveWindow.INVENTORY)

    wkspace = Workspace("Go Currency", wkspaces)
    wkspace.setPadding(15)
    return executeTasks, wkspace
