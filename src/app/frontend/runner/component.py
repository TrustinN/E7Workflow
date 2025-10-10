from .widget import RunnerWidget


class RunnerComponent:
    def __init__(self, widget: RunnerWidget):
        self.widget = widget

        self.widget.setLocalEntryBtn.clicked.connect()
        self.widget.setGlobalEntryBtn.clicked.connect()
        self.widget.restoreRunnerBtn.clicked.connect()
