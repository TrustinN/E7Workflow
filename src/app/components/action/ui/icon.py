from src.app.components.action.actions import ActionType


class ActionIconResolver:
    @staticmethod
    def resolveIcon(name, userParams):
        if name == ActionType.CLICK:
            return ":/action/icons/mouse-pointer-click.svg"
        elif name == ActionType.DRAG:
            direction = userParams["dir"]["value"]
            icons = {
                "up": ":/action/icons/move-up.svg",
                "down": ":/action/icons/move-down.svg",
                "left": ":/action/icons/move-left.svg",
                "right": ":/action/icons/move-right.svg",
            }
            return icons[direction]
        elif name == ActionType.CAPTURE:
            return ":/action/icons/focus.svg"

        raise RuntimeError()
