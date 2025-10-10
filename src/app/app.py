from PyQt5.QtWidgets import QApplication, QHBoxLayout, QMainWindow, QWidget

from src.router.routing import Dispatcher

from .frontend.context import Context
from .frontend.events import EventLog, EventType
from .frontend.graph import GraphController, GraphCore, GraphWidget
from .frontend.runner import RunnerWidget
from .frontend.workspace import WorkspaceController, WorkspaceCore, WorkspaceWidget


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

        self.context = Context()
        self.eventLog = EventLog()

        self.workspaceWidget = WorkspaceWidget()
        self.workspaceController = WorkspaceController()
        self.workspaceCore = WorkspaceCore(
            self.workspaceWidget,
            self.workspaceController,
            self.context,
            self.eventLog,
            dispatcher,
        )

        self.graphWidget = GraphWidget()
        self.graphController = GraphController()
        self.graphCore = GraphCore(
            self.graphWidget,
            self.graphController,
            self.context,
            self.eventLog,
            dispatcher,
        )

        self.runnerWidget = RunnerWidget()

        self.layout.addWidget(self.workspaceWidget)
        self.layout.addWidget(self.graphWidget)
        self.layout.addWidget(self.runnerWidget)

        self.eventLog.processEvent(EventType.APPLICATION_LOADED)
