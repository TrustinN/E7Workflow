from PyQt5.QtWidgets import QApplication, QHBoxLayout, QMainWindow, QPushButton, QWidget

from src.router.routing import Dispatcher

from .event.events import Event, EventLog, EventType
from .graph import GraphController, GraphWidget
from .workspace import WorkspaceController, WorkspaceWidget


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
        self.workspaceWidget = WorkspaceWidget()
        self.createWorkspaceBtn = QPushButton("Create Workspace")
        self.importBtn = QPushButton("Import")
        self.exportBtn = QPushButton("Export")

        self.layout.addWidget(self.graphWidget)
        self.layout.addWidget(self.workspaceWidget)
        self.layout.addWidget(self.createWorkspaceBtn)

        self.graphController = GraphController(
            self.eventLog, dispatcher, self.graphWidget
        )
        self.workspaceController = WorkspaceController(
            self.eventLog, dispatcher, self.workspaceWidget
        )

        self.createWorkspaceBtn.clicked.connect(
            self.workspaceController.createWorkspace
        )

        self.eventLog.processEvent(Event(EventType.APPLICATION_LOADED))
