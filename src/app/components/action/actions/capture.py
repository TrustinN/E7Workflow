import time

import mss
import numpy as np

from .action import Action
from .types import ActionType


class CaptureAction(Action):
    def __init__(self):
        super().__init__()

    @classmethod
    def info(cls):
        return {
            "name": ActionType.CAPTURE,
            "systemParams": {
                "tl": {"type": "point"},
                "br": {"type": "point"},
                "speed": {"type": "float"},
            },
            "userParams": {
                "sleep": {"type": "float"},
            },
            "result": {"capture": None},
        }

    def execute(self, data):
        systemParams = data["systemParams"]
        userParams = data["userParams"]
        tl = systemParams["tl"]
        br = systemParams["br"]

        x1, y1 = tl
        x2, y2 = br

        monitor = {
            "left": x1,
            "top": y1,
            "width": (x2 - x1 + 1),
            "height": (y2 - y1 + 1),
        }

        with mss.mss() as sct:
            screenshot = sct.grab(monitor)
            img = np.array(screenshot)
            img = img[:, :, [2, 1, 0]]
            img = np.ascontiguousarray(img)

            time.sleep(userParams["sleep"] * 1.0 / systemParams["speed"])
            return {"capture": img.astype(np.uint8)}
