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
            },
            "userParams": {},
        }

    def action(self, data):
        systemParams = data["systemParams"]
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

        return img[:, :, ::-1].astype(np.uint8)
