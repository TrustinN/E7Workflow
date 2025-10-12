from src.app.frontend.context import Context, ContextManager

from .widget import RunnerWidget


class RunnerComponent:
    def __init__(self, widget: RunnerWidget, ctxManager: ContextManager):
        self.widget = widget

        # self.widget.setLocalEntryBtn.clicked.connect()
        # self.widget.setGlobalEntryBtn.clicked.connect()
        # self.widget.restoreRunnerBtn.clicked.connect()

        self.ctxManager = ctxManager

    def onSetLocalEntry(self):
        self.context.get("workspaceViewMapping")
        self.context.get("workspaceNodeMapping")
