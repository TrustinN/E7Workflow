import time

from app import Workflow, Workspace

from .utils import click


def buildHomeWorkflow():

    wsNames = ["Focus", "Menu", "Home"]
    wkspaces = [Workspace(n) for n in wsNames]
    delays = [0.2] * len(wsNames)

    def executeTasks(state):
        for i in range(len(wkspaces)):
            click(wkspaces[i], state)
            time.sleep(delays[i])

    homeWorkflow = Workflow("Go Home", executeTasks, wkspaces)
    return homeWorkflow


def buildGrowthAltarWorkflow():

    wsNames = ["Focus", "Sanctuary", "Forest of Souls", "Growth Altar"]
    wkspaces = [Workspace(n) for n in wsNames]
    delays = [0.2, 3.0, 0.5, 0.5]

    def executeTasks(state):
        for i in range(len(wkspaces)):
            click(wkspaces[i], state)
            time.sleep(delays[i])

    gAWorkflow = Workflow("Go Growth Altar", executeTasks, wkspaces)
    return gAWorkflow


def buildShopWorkflow():
    wsNames = ["Focus", "Shop"]
    wkspaces = [Workspace(n) for n in wsNames]
    delays = [0.2] * len(wkspaces)

    def executeTasks(state):
        for i in range(len(wkspaces)):
            click(wkspaces[i], state)
            time.sleep(delays[i])

    workflow = Workflow("Go Shop", executeTasks, wkspaces)
    return workflow
