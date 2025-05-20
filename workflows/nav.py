import time

from app import Task, Workflow, Workspace

from .utils import click


def buildHomeWorkflow():
    focusTask = Task()
    focusWS = Workspace("Focus")

    menuTask = Task()
    menuWS = Workspace("Menu")

    homeTask = Task()
    homeWS = Workspace("Home")

    clickTasks = [focusTask, menuTask, homeTask]
    wkspaces = [focusWS, menuWS, homeWS]

    for i in range(len(clickTasks)):
        clickTasks[i].setWorkspace(wkspaces[i])
        clickTasks[i].setFunc(click)

    def executeTasks():
        state = {}
        for i in range(len(clickTasks)):
            clickTasks[i].execute(state)
            time.sleep(0.2)

        return state

    homeWorkflow = Workflow("Go Home", executeTasks, wkspaces)
    return homeWorkflow
