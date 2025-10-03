from PyQt5.QtWidgets import QApplication, QHBoxLayout, QMainWindow, QPushButton, QWidget

from src.router.routing import Dispatcher

from .event.events import EventLog, EventType
from .graph import GraphController, GraphCore, GraphWidget
from .workspace import WorkspaceController, WorkspaceCore, WorkspaceWidget


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
        self.graphController = GraphController(dispatcher)
        self.graphCore = GraphCore(
            self.graphWidget, self.graphController, self.eventLog
        )

        self.workspaceWidget = WorkspaceWidget()
        self.workspaceController = WorkspaceController(self.eventLog, dispatcher)
        self.workspaceCore = WorkspaceCore(
            self.workspaceWidget, self.workspaceController, self.eventLog
        )

        self.importBtn = QPushButton("Import")
        self.exportBtn = QPushButton("Export")

        self.layout.addWidget(self.graphWidget)
        self.layout.addWidget(self.workspaceWidget)

        self.eventLog.processEvent(EventType.APPLICATION_LOADED)
