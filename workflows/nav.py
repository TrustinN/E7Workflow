import time

from app import Task, Workflow, Workspace

from .utils import click


def buildHomeWorkflow():

    clickTaskNames = ["Focus", "Menu", "Home"]
    clickTasks = [Task() for i in range(len(clickTaskNames))]
    wkspaces = [Workspace(n) for n in clickTaskNames]
    delays = [0.2] * len(clickTaskNames)

    for i in range(len(clickTasks)):
        clickTasks[i].setWorkspace(wkspaces[i])
        clickTasks[i].setFunc(click)

    def executeTasks(state):
        for i in range(len(clickTasks)):
            clickTasks[i].execute(state)
            time.sleep(delays[i])

    homeWorkflow = Workflow("Go Home", executeTasks, wkspaces)
    return homeWorkflow


def buildGrowthAltarWorkflow():

    clickTaskNames = ["Focus", "Sanctuary", "Forest of Souls", "Growth Altar"]
    clickTasks = [Task() for i in range(len(clickTaskNames))]
    clickWS = [Workspace(n) for n in clickTaskNames]
    delays = [0.2, 3.0, 0.5, 0.5]

    for i in range(len(clickTasks)):
        clickTasks[i].setWorkspace(clickWS[i])
        clickTasks[i].setFunc(click)

    def executeTasks(state):
        for i in range(len(clickTasks)):
            clickTasks[i].execute(state)
            time.sleep(delays[i])

    gAWorkflow = Workflow("Go Growth Altar", executeTasks, clickWS)
    return gAWorkflow


def buildShopWorkflow():
    clickTaskNames = ["Focus", "Shop"]
    clickTasks = [Task() for i in range(len(clickTaskNames))]
    clickWS = [Workspace(n) for n in clickTaskNames]
    delays = [0.2] * len(clickTasks)

    for i in range(len(clickTasks)):
        clickTasks[i].setWorkspace(clickWS[i])
        clickTasks[i].setFunc(click)

    def executeTasks(state):
        for i in range(len(clickTasks)):
            clickTasks[i].execute(state)
            time.sleep(delays[i])

    workflow = Workflow("Go Shop", executeTasks, clickWS)
    return workflow
