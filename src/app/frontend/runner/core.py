from src.app.frontend.context import ContextManager
from src.app.frontend.events import PyQtSignalAdaptor

from .components import RunnerUI
from .context import RunnerContextManager
from .widget import RunnerWidget


class RunnerComponent:
    def __init__(self, ctxManager: ContextManager):
        self.ctxManager = RunnerContextManager(ctxManager)

        self.widget = RunnerWidget()
        self.runnerUI = RunnerUI(self.widget)

    def onSetLocalEntry(self):
        self.context.get("workspaceViewMapping")
        self.context.get("workspaceNodeMapping")

    def _initSignals(self):

        setLocalSignal = PyQtSignalAdaptor(self.runnerUI.setLocalEntry_)
        setGlobalSignal = PyQtSignalAdaptor(self.runnerUI.setGlobalEntry_)
        restoreSignal = PyQtSignalAdaptor(self.runnerUI.restore_)

        self.signals = {
            "setLocalSignal": setLocalSignal,
            "setGlobalSignal": setGlobalSignal,
            "restoreSignal": restoreSignal,
        }

        return self.signals
