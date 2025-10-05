from PyQt5.QtWidgets import QApplication, QHBoxLayout, QMainWindow, QWidget

from src.router.routing import Dispatcher

from .backend.graph import GraphController, GraphCore
from .backend.workspace import WorkspaceController, WorkspaceCore
from .event.events import EventLog, EventType
from .frontend.graph import GraphWidget
from .frontend.workspace import WorkspaceWidget


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

        self.eventLog = EventLog()

        self.graphWidget = GraphWidget()
        self.graphController = GraphController()
        self.graphCore = GraphCore(
            self.graphWidget,
            self.graphController,
            self.eventLog,
            dispatcher,
        )

        self.workspaceWidget = WorkspaceWidget()
        self.workspaceController = WorkspaceController()
        self.workspaceCore = WorkspaceCore(
            self.workspaceWidget,
            self.workspaceController,
            self.eventLog,
            dispatcher,
        )

        self.layout.addWidget(self.graphWidget)
        self.layout.addWidget(self.workspaceWidget)

        self.eventLog.processEvent(EventType.APPLICATION_LOADED)
