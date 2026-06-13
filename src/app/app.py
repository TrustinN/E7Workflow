from PyQt5.QtWidgets import QApplication, QHBoxLayout, QMainWindow, QVBoxLayout, QWidget

from src.router.routing import Dispatcher

from .frontend.capabilities import (
    Buttons,
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


class App(QApplication):
    def __init__(self, dispatcher: Dispatcher):
        super().__init__([])

        self.window = MainWindow()
        self.widget = QWidget()

        self.layout = QHBoxLayout()
        self.layoutLeft = QVBoxLayout()
        self.layoutRight = QVBoxLayout()
        self.layout.addLayout(self.layoutLeft)
        self.layout.addLayout(self.layoutRight)

        self.widget.setLayout(self.layout)
        self.window.setCentralWidget(self.widget)
        self.window.show()

        self.context = Context()
        self.document = Document()
        self.contextManager = StateManager(self.context, self.document)

        self.buttons = Buttons()
        self.wksCapability = WorkspaceCapability(self.context)
        self.graphCapability = GraphCapability(self.context)
        self.runnerCapability = RunnerCapability(self.context)
        self.serialCapability = SerializationCapability()

        self.buttons.createWorkspace_.connect(self.wksCapability.requestWorkspace)
        self.buttons.setE1Btn.clicked.connect(self.graphCapability.setE1)
        self.buttons.setE2Btn.clicked.connect(self.graphCapability.setE2)
        self.buttons.createEdgeBtn.clicked.connect(self.graphCapability.requestEdge)
        self.buttons.entryBtn.clicked.connect(self.runnerCapability.requestEntry)
        self.buttons.executeBtn.clicked.connect(self.runnerCapability.requestExecute)
        self.buttons.exportBtn.clicked.connect(self.serialCapability.handleExport)
        self.buttons.importBtn.clicked.connect(self.serialCapability.handleImport)

        self.wkCpt = WorkspaceComponent(self.context, self.document)
        self.graphCpt = GraphComponent(self.context, self.document)
        self.runnerCpt = RunnerComponent(self.context, self.document, dispatcher)

        self.layoutLeft.addWidget(self.graphCpt.widget)
        self.layoutLeft.addStretch()
        self.layoutRight.addWidget(self.buttons)
        self.layoutRight.addWidget(self.runnerCpt.widget)
        self.layoutRight.addStretch()

        self.pubSubHandler = PubSubHandler()
        self.pubSubHandler.registerNode(self.contextManager)

        self.pubSubHandler.registerNode(self.wksCapability)
        self.pubSubHandler.registerNode(self.graphCapability)
        self.pubSubHandler.registerNode(self.runnerCapability)
        self.pubSubHandler.registerNode(self.serialCapability)

        self.pubSubHandler.registerNode(self.wkCpt)
        self.pubSubHandler.registerNode(self.graphCpt)
        self.pubSubHandler.registerNode(self.runnerCpt)
        self.pubSubHandler.handlePublish("/App/Loaded")
