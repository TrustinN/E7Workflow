from PyQt5.QtWidgets import QApplication, QHBoxLayout, QMainWindow, QWidget

from src.router.routing import Dispatcher

from .frontend.context import ContextManager
from .frontend.events import AppEvents, EventLog
from .frontend.graph import GraphComponent
from .frontend.runner import RunnerComponent
from .frontend.workspace import WorkspaceComponent


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

        self.wkCpt = WorkspaceComponent(self.ctxManager, self.eventLog, dispatcher)
        self.graphCpt = GraphComponent(self.ctxManager, self.eventLog, dispatcher)
        self.runnerCpt = RunnerComponent(self.ctxManager)

        self.layout.addWidget(self.wkCpt.widget)
        self.layout.addWidget(self.graphCpt.widget)
        self.layout.addWidget(self.runnerCpt.widget)

        self.eventLog.processEvent(AppEvents.APP_LOADED)
