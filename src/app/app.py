from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QMainWindow,
    QPushButton,
    QShortcut,
    QVBoxLayout,
    QWidget,
)

from src.router.routing import Dispatcher

from .frontend.capabilities import (
    GraphCapability,
    RunnerCapability,
    SerializationCapability,
    WorkspaceCapability,
)
from .frontend.events import PubSubHandler
from .frontend.state import Context, Document, StateManager
from .frontend.widgets.graph import GraphComponent
from .frontend.widgets.runner import RunnerComponent
from .frontend.widgets.workspace import WorkspaceComponent


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

    def closeEvent(self, event):
        QApplication.quit()


def setButtonText(button, text, shortcut):
    key = shortcut.key().toString(QKeySequence.NativeText)
    button.setText(f"{text} ({key})")


class App(QApplication):
    def __init__(self, dispatcher: Dispatcher):
        super().__init__([])

        self._initState()
        self._initComponents(self.context, self.document, dispatcher)
        self._initLayout()
        self._initShortcuts()
        self._initCapabilities(self.context)
        self._initSignals()

        self.pubSubHandler = PubSubHandler()
        self.pubSubHandler.registerNode(self.contextManager)
        self.pubSubHandler.registerNodes(self.capabilites)
        self.pubSubHandler.registerNodes(self.components)
        self.pubSubHandler.handlePublish("/App/Loaded")

    def _initState(self):
        self.context = Context()
        self.document = Document()
        self.contextManager = StateManager(self.context, self.document)

    def _initCapabilities(self, context: Context):
        self.wksCapability = WorkspaceCapability(context)
        self.graphCapability = GraphCapability(context)
        self.runnerCapability = RunnerCapability(context)
        self.serialCapability = SerializationCapability()
        self.capabilites = [
            self.wksCapability,
            self.graphCapability,
            self.runnerCapability,
            self.serialCapability,
        ]

    def _initComponents(self, context, document, dispatcher):
        self.wkCpt = WorkspaceComponent(context, document)
        self.graphCpt = GraphComponent(context, document)
        self.runnerCpt = RunnerComponent(context, document, dispatcher)

        self.components = [self.wkCpt, self.graphCpt, self.runnerCpt]

    def _initShortcuts(self):
        self.workspaceShortcut = QShortcut(QKeySequence.New, self.window)
        self.setE1Shortcut = QShortcut(QKeySequence("1"), self.window)
        self.setE2Shortcut = QShortcut(QKeySequence("2"), self.window)
        self.createEdgeShortcut = QShortcut(QKeySequence("E"), self.window)
        self.entryShortcut = QShortcut(QKeySequence("Return"), self.window)
        self.executeShortcut = QShortcut(QKeySequence("Ctrl+R"), self.window)
        self.exportShortcut = QShortcut(QKeySequence.Save, self.window)
        self.importShortcut = QShortcut(QKeySequence.Open, self.window)

        self.workspaceShortcut.setContext(Qt.ApplicationShortcut)
        self.setE1Shortcut.setContext(Qt.ApplicationShortcut)
        self.setE2Shortcut.setContext(Qt.ApplicationShortcut)
        self.createEdgeShortcut.setContext(Qt.ApplicationShortcut)
        self.entryShortcut.setContext(Qt.ApplicationShortcut)
        self.executeShortcut.setContext(Qt.ApplicationShortcut)
        self.exportShortcut.setContext(Qt.ApplicationShortcut)
        self.importShortcut.setContext(Qt.ApplicationShortcut)

        setButtonText(self.wksBtn, "Create Workspace", self.workspaceShortcut)
        setButtonText(self.setE1Btn, "Set Edge Start", self.setE1Shortcut)
        setButtonText(self.setE2Btn, "Set Edge End", self.setE2Shortcut)
        setButtonText(self.createEdgeBtn, "Create Edge", self.createEdgeShortcut)
        setButtonText(self.entryBtn, "Set Entry", self.entryShortcut)
        setButtonText(self.executeBtn, "Execute", self.executeShortcut)
        setButtonText(self.exportBtn, "Export", self.exportShortcut)
        setButtonText(self.importBtn, "Import", self.importShortcut)

    def _initSignals(self):
        actions = {
            self.wksCapability.requestWorkspace: [
                self.wksBtn.clicked,
                self.workspaceShortcut.activated,
            ],
            self.graphCapability.setE1: [
                self.setE1Btn.clicked,
                self.setE1Shortcut.activated,
            ],
            self.graphCapability.setE2: [
                self.setE2Btn.clicked,
                self.setE2Shortcut.activated,
            ],
            self.graphCapability.requestEdge: [
                self.createEdgeBtn.clicked,
                self.createEdgeShortcut.activated,
            ],
            self.runnerCapability.requestEntry: [
                self.entryBtn.clicked,
                self.entryShortcut.activated,
            ],
            self.runnerCapability.requestExecute: [
                self.executeBtn.clicked,
                self.executeShortcut.activated,
            ],
            self.serialCapability.handleExport: [
                self.exportBtn.clicked,
                self.exportShortcut.activated,
            ],
            self.serialCapability.handleImport: [
                self.importBtn.clicked,
                self.importShortcut.activated,
            ],
        }

        for slot, signals in actions.items():
            for signal in signals:
                signal.connect(slot)

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

        self.layoutLeft.addWidget(self.graphCpt.widget)
        self.layoutLeft.addStretch()

        self.wksBtn = QPushButton()
        self.setE1Btn = QPushButton()
        self.setE2Btn = QPushButton()
        self.createEdgeBtn = QPushButton()
        self.entryBtn = QPushButton()
        self.executeBtn = QPushButton()
        self.exportBtn = QPushButton()
        self.importBtn = QPushButton()

        self.layoutMid.addWidget(self.wksBtn)
        self.layoutMid.addWidget(self.setE1Btn)
        self.layoutMid.addWidget(self.setE2Btn)
        self.layoutMid.addWidget(self.createEdgeBtn)
        self.layoutMid.addWidget(self.entryBtn)
        self.layoutMid.addWidget(self.executeBtn)
        self.layoutMid.addWidget(self.exportBtn)
        self.layoutMid.addWidget(self.importBtn)
        self.layoutMid.addWidget(self.runnerCpt.actionEditor)
        self.layoutMid.addStretch()

        self.layoutRight.addWidget(self.runnerCpt.edgeEditor)
        self.layoutRight.addStretch()
