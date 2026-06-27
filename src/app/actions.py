from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QAction


class ActionRegistry:
    def __init__(self):
        self.actions: dict[str, QAction] = {}

    def register(self, name: str, action: QAction):
        self.actions[name] = action

    def get(self, name: str) -> QAction:
        return self.actions[name]

    def shortcutText(self, name: str) -> str:
        action = self.actions[name]
        seq = action.shortcut()
        return seq.toString(QKeySequence.NativeText) if not seq.isEmpty() else ""

    def label(self, name: str) -> str:
        return self.actions[name].text()

    def displayText(self, name: str) -> str:
        action = self.actions[name]
        key = action.shortcut().toString(QKeySequence.NativeText)

        if key:
            return f"{action.text()} ({key})"
        return action.text()
