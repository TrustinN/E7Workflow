import pyautogui

from .action import Action


class DragAction(Action):
    def __init__(self):
        super().__init__("Drag")

    def info():
        return {
            "name": "Drag",
            "system_params": {
                "tl": {"type": "point"},
                "br": {"type": "point"},
            },
            "user_params": {
                "dir": {
                    "type": "enum",
                    "values": ["up", "down", "left", "right"],
                }
            },
        }

    def action(self, data):
        userParams = data["user_params"]
        systemParams = data["system_params"]

        direction = userParams["dir"]
        tl = systemParams["tl"]
        br = systemParams["br"]

        x1, y1 = tl
        x2, y2 = br
        xmid = (x1 + x2) / 2
        ymid = (y1 + y2) / 2

        start, end = None, None

        if direction == "down":
            start = (xmid, y1)
            end = (xmid, y2)

        elif direction == "up":
            start = (xmid, y2)
            end = (xmid, y1)

        elif direction == "right":
            start = (x1, ymid)
            end = (x2, ymid)

        else:  # left
            start = (x2, ymid)
            end = (x1, ymid)

        scrollTime = 0.3
        scrollAnim = pyautogui.easeOutQuad
        scrollClick = "left"

        pyautogui.moveTo(*start)
        pyautogui.dragTo(*end, scrollTime, scrollAnim, button=scrollClick)
