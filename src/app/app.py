from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import (
    QAction,
    QApplication,
    QHBoxLayout,
    QMainWindow,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from src.router.routing import Dispatcher

from .components.action import ActionComponent
from .components.graph import GraphComponent
from .components.runner import RunnerComponent
from .components.script import ScriptComponent
from .components.workspace import WorkspaceComponent
from .events import EventBus
from .serialization import SerializerNode
from .state import Context, ContextManager


class MainWindow(QMainWindow):
    requestExport = pyqtSignal()
    requestImport = pyqtSignal()

    def __init__(self):
        super().__init__()
        fileMenu = self.menuBar().addMenu("&File")

        saveAction = QAction("Save", self)
        saveAction.setShortcut(QKeySequence.Save)
        saveAction.triggered.connect(self.requestExport.emit)

        loadAction = QAction("Open...", self)
        loadAction.setShortcut(QKeySequence.Open)
        loadAction.triggered.connect(self.requestImport.emit)

        fileMenu.addAction(loadAction)
        fileMenu.addAction(saveAction)

    def closeEvent(self, event):
        QApplication.quit()


class App(QApplication):
    def __init__(self, dispatcher: Dispatcher):
        super().__init__([])

        self._initState()
        self._initComponents(self.context, dispatcher)
        self._initLayout()

        self.serializerNode = SerializerNode(self.context)
        self.window.requestExport.connect(self.serializerNode.handleExport)
        self.window.requestImport.connect(self.serializerNode.handleImport)

        self.eventBus = EventBus()
        self.eventBus.registerNode(self.contextManager)
        self.eventBus.registerNode(self.serializerNode)
        self.eventBus.registerNodes(self.components)
        self.eventBus.handlePublish("/App/Loaded")

    def _initState(self):
        self.context = Context()
        self.contextManager = ContextManager(self.context)

    def _initComponents(self, context, dispatcher):
        self.wkCpt = WorkspaceComponent(context, dispatcher)
        self.graphCpt = GraphComponent(context, dispatcher)
        self.actionCpt = ActionComponent(context, dispatcher)
        self.scriptCpt = ScriptComponent(context, dispatcher)
        self.runnerCpt = RunnerComponent(context, dispatcher)

        self.components = [
            self.wkCpt,
            self.graphCpt,
            self.actionCpt,
            self.scriptCpt,
            self.runnerCpt,
        ]

    def _initLayout(self):
        self.window = MainWindow()
        self.widget = QWidget()

        self.layout = QHBoxLayout(self.widget)
        self.layoutLeft = QVBoxLayout()
        self.layoutMid = QVBoxLayout()
        self.layoutRight = QVBoxLayout()
        self.layout.addLayout(self.layoutLeft)
        self.layout.addLayout(self.layoutMid)
        self.layout.addLayout(self.layoutRight)

        self.window.setCentralWidget(self.widget)
        self.window.show()

        self.layoutLeft.addStretch()

        self.layoutMid.addWidget(self.wkCpt.editor)
        self.layoutMid.addWidget(self.graphCpt.editor)
        self.layoutMid.addStretch()

        self.tabs = QTabWidget()
        self.tabs.addTab(self.wkCpt.editor, "Workspaces")
        self.tabs.addTab(self.actionCpt.editor, "Actions")
        self.tabs.addTab(self.scriptCpt.editor, "Scripts")

        self.layoutRight.addWidget(self.runnerCpt.editor)
        self.layoutRight.addWidget(self.tabs)
        self.layoutRight.addStretch()
