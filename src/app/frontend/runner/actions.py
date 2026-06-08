import time

import numpy as np
import pyautogui
from PyQt5.QtCore import QPoint

from app import Workspace


def ptToTuple(pt):
    x, y = pt.x(), pt.y()
    return (x, y)


def tupleToPt(arry):
    x, y = arry
    return QPoint(x, y)


DEFAULT_SLEEP_TIME = 0.3


def execAndSleep(func, *args, sleep=DEFAULT_SLEEP_TIME, **kwargs):
    func(*args, **kwargs)
    time.sleep(sleep)


def click(wks: Workspace, **kwargs):
    tl, br = wks.getBBox()
    tl = ptToTuple(tl)
    br = ptToTuple(br)
    mid = (np.array(tl) + np.array(br)) / 2
    pyautogui.click(int(mid[0]), int(mid[1]))


def scroll(wks: Workspace, **kwargs):
    dir = kwargs["dir"]
    tl, br = wks.getBBox()
    tl = ptToTuple(tl)
    br = ptToTuple(br)

    scrollTime = 0.3
    scrollAnim = pyautogui.easeOutQuad
    scrollClick = "left"

    x1, y1 = tl
    x2, y2 = br
    if dir in ["up", "down"]:
        xmid = (x1 + x2) / 2
        if dir == "down":
            pyautogui.moveTo(xmid, y1)
            pyautogui.dragTo(xmid, y2, scrollTime, scrollAnim, button=scrollClick)
        else:
            pyautogui.moveTo(xmid, y2)
            pyautogui.dragTo(xmid, y1, scrollTime, scrollAnim, button=scrollClick)
    else:
        ymid = (y1 + y2) / 2
        if dir == "right":
            pyautogui.moveTo(x1, ymid)
            pyautogui.dragTo(x2, ymid, scrollTime, scrollAnim, button=scrollClick)
        else:
            pyautogui.moveTo(x2, ymid)
            pyautogui.dragTo(x1, ymid, scrollTime, scrollAnim, button=scrollClick)
