from src.app.frontend.context import ContextManager

from .context import RunnerContextManager
from .widget import RunnerWidget


class RunnerComponent:
    def __init__(self, ctxManager: ContextManager):
        self.widget = RunnerWidget()
        self.ctxManager = RunnerContextManager(ctxManager)

        # self.widget.setLocalEntryBtn.clicked.connect()
        # self.widget.setGlobalEntryBtn.clicked.connect()
        # self.widget.restoreRunnerBtn.clicked.connect()

    def onSetLocalEntry(self):
        self.context.get("workspaceViewMapping")
        self.context.get("workspaceNodeMapping")
