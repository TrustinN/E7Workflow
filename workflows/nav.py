import time

from app import Workspace
from assets import ActiveWindow

from .utils import click

ACTIVE_WINDOW = "winActive"


def buildHomeWorkflow():

    wsNames = ["Focus", "Menu", "Home"]
    wkspaces = [Workspace(n) for n in wsNames]
    delays = [0.2] * len(wsNames)

    def executeTasks(state):
        for i in range(len(wkspaces)):
            click(wkspaces[i], state)
            time.sleep(delays[i])
        state[ACTIVE_WINDOW] = ActiveWindow.HOME

    wkspace = Workspace("Go Home", wkspaces)
    wkspace.setPadding(15)
    return executeTasks, wkspace


def buildGrowthAltarWorkflow():

    wsNames = ["Focus", "Sanctuary", "Forest of Souls", "Growth Altar"]
    wkspaces = [Workspace(n) for n in wsNames]
    delays = [0.2, 3.0, 0.5, 0.5]

    def executeTasks(state):
        for i in range(len(wkspaces)):
            click(wkspaces[i], state)
            time.sleep(delays[i])
        state[ACTIVE_WINDOW] = ActiveWindow.GROWTH_ALTAR

    wkspace = Workspace("Go Growth Altar", wkspaces)
    wkspace.setPadding(15)
    return executeTasks, wkspace


def buildShopWorkflow():
    wsNames = ["Focus", "Shop"]
    wkspaces = [Workspace(n) for n in wsNames]
    delays = [0.2] * len(wkspaces)

    def executeTasks(state):
        for i in range(len(wkspaces)):
            click(wkspaces[i], state)
            time.sleep(delays[i])
        state[ACTIVE_WINDOW] = ActiveWindow.SHOP

    wkspace = Workspace("Go Shop", wkspaces)
    wkspace.setPadding(15)
    return executeTasks, wkspace
