from enum import Enum

from workflows.state import GlobalState, StateManager

SCOPE = "Window Scope"
ACTIVE_WINDOW = "Active Window"


class ActiveWindow(Enum):
    HOME = "Home"
    GROWTH_ALTAR = "Growth Altar"
    SECRET_SHOP = "Secret Shop"
    INVENTORY = "Inventory"

    def __init__(self, name):
        self._name = name

    @property
    def name(self):
        return self._name


class WindowManager(StateManager):
    def __init__(self, scope):
        super().__init__(scope)

    def initState(self):
        super().initState()
        wState = self.state.getWorkflowState(self.scope)
        wState.setState(ACTIVE_WINDOW, "")

    def setActiveWindow(self, window):
        wState = self.state.getWorkflowState(self.scope)
        wState.setState(ACTIVE_WINDOW, window)

    def getActiveWindow(self):
        wState = self.state.getWorkflowState(self.scope)
        return wState.getState(ACTIVE_WINDOW)


windowManager = WindowManager(SCOPE)
