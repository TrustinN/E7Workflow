import os

SAVE_DIR = "saves"
ICON_DIR = "assets/icons"


class Icons:
    CLICK = os.path.join(ICON_DIR, "mouse-pointer-click.svg")
    DRAG_DOWN = os.path.join(ICON_DIR, "move-down.svg")
    DRAG_LEFT = os.path.join(ICON_DIR, "move-left.svg")
    DRAG_RIGHT = os.path.join(ICON_DIR, "move-right.svg")
    DRAG_UP = os.path.join(ICON_DIR, "move-up.svg")

    DRAG = {
        "up": DRAG_UP,
        "down": DRAG_DOWN,
        "left": DRAG_LEFT,
        "right": DRAG_RIGHT,
    }


def getIconPath(data):
    name = data["name"]
    userParams = data["userParams"]
    match name:
        case "Click":
            return Icons.CLICK

        case "Drag":
            direction = userParams["dir"]["value"]
            return Icons.DRAG[direction]
