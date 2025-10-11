from src.app.frontend.context import Context

from .widget import RunnerWidget


class RunnerComponent:
    def __init__(self, widget: RunnerWidget, context: Context):
        self.widget = widget

        # self.widget.setLocalEntryBtn.clicked.connect()
        # self.widget.setGlobalEntryBtn.clicked.connect()
        # self.widget.restoreRunnerBtn.clicked.connect()

        self.context = context

    def onSetLocalEntry(self):
        self.context.get("workspaceViewMapping")
        self.context.get("workspaceNodeMapping")
