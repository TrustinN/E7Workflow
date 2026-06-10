import numpy as np
import pyautogui

from .action import Action


class ClickAction(Action):
    def __init__(self):
        super().__init__("Click")

    def info():
        return {
            "name": "Click",
            "systemParams": {
                "tl": {"type": "point"},
                "br": {"type": "point"},
            },
            "userParams": {},
        }

    def action(self, data):
        systemParams = data["systemParams"]
        tl = systemParams["tl"]
        br = systemParams["br"]
        mid = (np.array(tl) + np.array(br)) / 2
        pyautogui.click(int(mid[0]), int(mid[1]))
