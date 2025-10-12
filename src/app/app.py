from PyQt5.QtWidgets import QApplication, QHBoxLayout, QMainWindow, QWidget

from src.router.routing import Dispatcher

from .frontend.context import ContextManager
from .frontend.events import AppEvents, EventLog
from .frontend.graph import GraphCore, GraphWidget
from .frontend.runner import RunnerComponent, RunnerWidget
from .frontend.workspace import WorkspaceCore, WorkspaceWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

    def closeEvent(self, event):
        QApplication.quit()


class App(QApplication):
    def __init__(self, dispatcher: Dispatcher):
        super().__init__([])

        self.window = MainWindow()
        self.widget = QWidget()
        self.layout = QHBoxLayout()
        self.widget.setLayout(self.layout)
        self.window.setCentralWidget(self.widget)
        self.window.show()

        self.ctxManager = ContextManager()
        self.eventLog = EventLog()

        self.workspaceWidget = WorkspaceWidget()
        self.workspaceCore = WorkspaceCore(
            self.workspaceWidget,
            self.ctxManager,
            self.eventLog,
            dispatcher,
        )

        self.graphWidget = GraphWidget()
        self.graphCore = GraphCore(
            self.graphWidget,
            self.ctxManager,
            self.eventLog,
            dispatcher,
        )

        self.runnerWidget = RunnerWidget()
        self.runnerComponent = RunnerComponent(self.runnerWidget, self.ctxManager)

        self.layout.addWidget(self.workspaceWidget)
        self.layout.addWidget(self.graphWidget)
        self.layout.addWidget(self.runnerWidget)

        self.eventLog.processEvent(AppEvents.APP_LOADED)
