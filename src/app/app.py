from PyQt5.QtWidgets import QApplication, QHBoxLayout, QMainWindow, QWidget

from src.app.frontend.workspace.events import WKEvents
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

        self._registerCapabilities()

        self.eventLog.processEvent(AppEvents.APP_LOADED)

    def _registerCapabilities(self):
        graphCreateRoot = self.graphCpt.useAction(self.graphCpt.CREATE_ROOT)
        graphCreate = self.graphCpt.useAction(self.graphCpt.CREATE_SCENE)
        graphUpdateNode = self.graphCpt.useAction(self.graphCpt.UPDATE_NODE)
        graphFocus = self.graphCpt.useAction(self.graphCpt.ON_FOCUS)
        graphExport = self.graphCpt.useAction(self.graphCpt.EXPORT)
        graphImport = self.graphCpt.useAction(self.graphCpt.IMPORT)

        self.eventLog.register(WKEvents.WK_CREATED_ROOT, graphCreateRoot)
        self.eventLog.register(WKEvents.WK_CREATED, graphCreate)
        self.eventLog.register(WKEvents.WK_UPDATED, graphUpdateNode)
        self.eventLog.register(WKEvents.WK_FOCUSED, graphFocus)
        self.eventLog.register(WKEvents.WK_EXPORTED, graphExport)
        self.eventLog.register(WKEvents.WK_IMPORTED, graphImport)
