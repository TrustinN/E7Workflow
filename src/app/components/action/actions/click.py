import time

import numpy as np
import pyautogui

from .action import Action
from .types import ActionType


class ClickAction(Action):
    def __init__(self):
        super().__init__()

    @classmethod
    def info(cls):
        return {
            "name": ActionType.CLICK,
            "systemParams": {
                "tl": {"type": "point"},
                "br": {"type": "point"},
            },
            "userParams": {
                "sleep": {"type": "float"},
            },
            "result": {},
        }

    def execute(self, data):
        systemParams = data["systemParams"]
        userParams = data["userParams"]

        tl = systemParams["tl"]
        br = systemParams["br"]
        mid = (np.array(tl) + np.array(br)) / 2
        pyautogui.click(int(mid[0]), int(mid[1]))

        time.sleep(userParams["sleep"])
        return {}
