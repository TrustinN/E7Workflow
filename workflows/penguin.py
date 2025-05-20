import time

import cv2
import pytesseract
import skimage.io as skio

from app import Task, Workflow, Workspace, WorkspaceLayout
from assets import getPenguinIcon, penguinTypes

from .utils import click, imageMatch, scan, screenshot

focusTask = Task()
focusWS = Workspace("Focus")

buyTask = Task()
buyWS = Workspace("Buy")

maxTask = Task()
maxWS = Workspace("Max")

confirmTask = Task()
confirmWS = Workspace("Confirm")


def findPenguin(wkspace, state, **kwargs):
    pgnIcon = getPenguinIcon(kwargs["pType"])
    state = imageMatch(wkspace, state, pgnIcon)
    if state["temp"]["result"]:
        state = getNumber(wkspace, state, **kwargs)
        state = updateStats(state)
    return state


def findPenguins(wkspace, state, **kwargs):
    for pType in penguinTypes:
        state = findPenguin(wkspace, state, pType=pType)
    return state


penguinScanTasks = [Task() for i in range(len(penguinTypes))]
penguinScanStartWS = Workspace("Scan Start")
penguinScanEndWS = Workspace("Scan End")
penguinScanPath = WorkspaceLayout("Scan Path", [penguinScanStartWS, penguinScanEndWS])
penguinScanPath.setPadding(0)

scanTasks = [Task() for i in range(len(penguinTypes))]

for i in range(len(penguinTypes)):
    scanTasks[i].setFunc(findPenguins, pType=penguinTypes[i])
    penguinScanTasks[i].setWorkspace(penguinScanStartWS)
    penguinScanTasks[i].setFunc(
        scan, parent=penguinScanPath, count=5, dir="horizontal", task=scanTasks[i]
    )

exitTask = Task()
exitWS = Workspace("Exit")

clickTasks = [focusTask, buyTask, maxTask, confirmTask, exitTask]
wkspaces = [focusWS, buyWS, maxWS, confirmWS, exitWS, penguinScanPath]


def getNumber(wkspace, state, **kwargs):
    tl, br = wkspace.getBBox()
    frame = wkspace.window.frameGeometry()
    region = (tl.x(), tl.y(), frame.width(), frame.height())

    image = screenshot(region)
    pType = kwargs["pType"]
    _, binaryImage = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY)
    # skio.imsave(f"{pType.name} {region}.png", binaryImage)

    text = pytesseract.image_to_string(binaryImage, config="--psm 6 digits")
    if text == "":
        text = "1"
    state["temp"]["result"] = int(text)
    state["temp"]["resultType"] = kwargs["pType"]
    return state


def updateStats(state):
    if "penguinStats" not in state:
        state["penguinStats"] = dict(zip(penguinTypes, [0] * len(penguinTypes)))

    pType = state["temp"]["resultType"]
    state["penguinStats"][pType] += state["temp"]["result"]

    return state


for i in range(len(clickTasks)):
    clickTasks[i].setWorkspace(wkspaces[i])
    clickTasks[i].setFunc(click)


def executeTasks(state):
    state["temp"] = {}
    for i in range(len(clickTasks) - 1):
        state = clickTasks[i].execute(state)
        time.sleep(0.2)

    for i in range(len(penguinTypes)):
        state = penguinScanTasks[i].execute(state)
        # print(state)

    # time.sleep(0.4)
    # exitTask.execute(state)
    time.sleep(0.2)

    return state


penguinWorkflow = Workflow("Penguin", executeTasks, wkspaces)
