from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import (
    QAction,
    QApplication,
    QHBoxLayout,
    QMainWindow,
    QVBoxLayout,
    QWidget,
)

from src.router.routing import Dispatcher

from .components.graph import GraphComponent
from .components.workspace import WorkspaceComponent
from .events import PubSubHandler
from .serialization import SerializerNode
from .state import Context


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


def setButtonText(button, text, shortcut):
    key = shortcut.key().toString(QKeySequence.NativeText)
    button.setText(f"{text} ({key})")


class App(QApplication):
    def __init__(self, dispatcher: Dispatcher):
        super().__init__([])

        self._initState()
        self._initComponents(self.context, dispatcher)
        self._initLayout()

        self.serializerNode = SerializerNode(self.context)
        self.window.requestExport.connect(self.serializerNode.handleExport)
        self.window.requestImport.connect(self.serializerNode.handleImport)

        self.pubSubHandler = PubSubHandler()
        self.pubSubHandler.registerNode(self.serializerNode)
        self.pubSubHandler.registerNodes(self.components)
        self.pubSubHandler.handlePublish("/App/Loaded")

    def _initState(self):
        self.context = Context()

    def _initComponents(self, context, dispatcher):
        self.wkCpt = WorkspaceComponent(context)
        self.graphCpt = GraphComponent(context)
        # self.runnerCpt = RunnerComponent(context, document, dispatcher)

        self.components = [
            self.wkCpt,
            self.graphCpt,
            # self.runnerCpt,
        ]

    # def _initShortcuts(self):
    # self.entryShortcut = QShortcut(QKeySequence("Return"), self.window)
    # self.executeShortcut = QShortcut(QKeySequence("Ctrl+R"), self.window)
    # self.exportShortcut = QShortcut(QKeySequence.Save, self.window)
    # self.importShortcut = QShortcut(QKeySequence.Open, self.window)

    # self.entryShortcut.setContext(Qt.ApplicationShortcut)
    # self.executeShortcut.setContext(Qt.ApplicationShortcut)
    # self.exportShortcut.setContext(Qt.ApplicationShortcut)
    # self.importShortcut.setContext(Qt.ApplicationShortcut)

    # setButtonText(self.entryBtn, "Set Entry", self.entryShortcut)
    # setButtonText(self.executeBtn, "Execute", self.executeShortcut)
    # setButtonText(self.exportBtn, "Export", self.exportShortcut)
    # setButtonText(self.importBtn, "Import", self.importShortcut)

    # def _initSignals(self):
    #     actions = {
    #         # self.wksCapability.requestWorkspace: [
    #         #     self.wksBtn.clicked,
    #         #     self.workspaceShortcut.activated,
    #         # ],
    #         # self.graphCapability.setE1: [
    #         #     self.setE1Btn.clicked,
    #         #     self.setE1Shortcut.activated,
    #         # ],
    #         # self.graphCapability.setE2: [
    #         #     self.setE2Btn.clicked,
    #         #     self.setE2Shortcut.activated,
    #         # ],
    #         # self.graphCapability.requestEdge: [
    #         #     self.createEdgeBtn.clicked,
    #         #     self.createEdgeShortcut.activated,
    #         # ],
    #         # self.runnerCapability.requestEntry: [
    #         #     self.entryBtn.clicked,
    #         #     self.entryShortcut.activated,
    #         # ],
    #         # self.runnerCapability.requestExecute: [
    #         #     self.executeBtn.clicked,
    #         #     self.executeShortcut.activated,
    #         # ],
    #         # self.serialCapability.handleExport: [
    #         #     self.exportBtn.clicked,
    #         #     self.exportShortcut.activated,
    #         # ],
    #         # self.serialCapability.handleImport: [
    #         #     self.importBtn.clicked,
    #         #     self.importShortcut.activated,
    #         # ],
    #     }
    #
    #     for slot, signals in actions.items():
    #         for signal in signals:
    #             signal.connect(slot)

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

        # self.layoutLeft.addWidget(self.graphCpt.widget)
        self.layoutLeft.addStretch()

        # self.entryBtn = QPushButton()
        # self.executeBtn = QPushButton()
        # self.exportBtn = QPushButton()
        # self.importBtn = QPushButton()

        self.layoutMid.addWidget(self.wkCpt.editor)
        self.layoutMid.addWidget(self.graphCpt.editor)
        # self.layoutMid.addWidget(self.entryBtn)
        # self.layoutMid.addWidget(self.executeBtn)
        # self.layoutMid.addWidget(self.exportBtn)
        # self.layoutMid.addWidget(self.importBtn)
        # self.layoutMid.addWidget(self.runnerCpt.actionEditor)
        self.layoutMid.addStretch()

        # self.layoutRight.addWidget(self.runnerCpt.edgeEditor)
        self.layoutRight.addStretch()
