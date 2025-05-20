import time

from app import Task, Workflow, Workspace

from .utils import click


def buildWorkflow():
    focusTask = Task()
    focusWS = Workspace("Focus")

    buyTask = Task()
    buyWS = Workspace("Buy")

    maxTask = Task()
    maxWS = Workspace("Max")

    confirmTask = Task()
    confirmWS = Workspace("Confirm")

    exitTask = Task()
    exitWS = Workspace("Exit")

    clickTasks = [focusTask, buyTask, maxTask, confirmTask, exitTask]
    wkspaces = [focusWS, buyWS, maxWS, confirmWS, exitWS]

    for i in range(len(clickTasks)):
        clickTasks[i].setWorkspace(wkspaces[i])
        clickTasks[i].setFunc(click)

    def executeTasks():
        state = {}
        for i in range(len(clickTasks) - 1):
            clickTasks[i].execute(state)
            time.sleep(0.2)

        time.sleep(0.4)
        exitTask.execute(state)
        time.sleep(0.2)

        return state

    penguinWorkflow = Workflow("Penguin", executeTasks, wkspaces)
    return penguinWorkflow
