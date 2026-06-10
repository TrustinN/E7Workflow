from PyQt5.QtWidgets import QApplication, QHBoxLayout, QMainWindow, QVBoxLayout, QWidget

from src.router.routing import Dispatcher

from .frontend.capabilities import (
    Buttons,
    GraphCapability,
    RunnerCapability,
    WorkspaceCapability,
)
from .frontend.events import PubSubHandler
from .frontend.state import WorkspaceContext, WorkspaceContextManager
from .frontend.widgets.graph import GraphComponent
from .frontend.widgets.runner import RunnerComponent
from .frontend.widgets.serialization import SerializationComponent
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

        self.context = WorkspaceContext()
        self.contextManager = WorkspaceContextManager(self.context)

        self.buttons = Buttons()
        self.wksCapability = WorkspaceCapability()
        self.graphCapability = GraphCapability()
        self.runnerCapability = RunnerCapability()

        self.buttons.createWorkspace_.connect(self.wksCapability.createWorkspace)
        self.buttons.createEdgeBtn.clicked.connect(self.graphCapability.createEdge)
        self.buttons.entryBtn.clicked.connect(self.runnerCapability.requestEntry)
        self.buttons.executeBtn.clicked.connect(self.runnerCapability.requestExecute)

        self.wkCpt = WorkspaceComponent(self.context)
        self.graphCpt = GraphComponent(self.context)
        self.runnerCpt = RunnerComponent(self.context, dispatcher)
        self.serialCpt = SerializationComponent()

        self.layoutLeft.addWidget(self.graphCpt)
        self.layoutLeft.addStretch()
        self.layoutRight.addWidget(self.buttons)
        self.layoutRight.addWidget(self.serialCpt)
        self.layoutRight.addWidget(self.runnerCpt)
        self.layoutRight.addStretch()

        self.pubSubHandler = PubSubHandler()
        self.pubSubHandler.registerNode(self.contextManager)

        self.pubSubHandler.registerNode(self.wksCapability)
        self.pubSubHandler.registerNode(self.graphCapability)
        self.pubSubHandler.registerNode(self.runnerCapability)

        self.pubSubHandler.registerNode(self.wkCpt.node)
        self.pubSubHandler.registerNode(self.graphCpt.node)
        self.pubSubHandler.registerNode(self.runnerCpt.node)
        self.pubSubHandler.registerNode(self.serialCpt.node)
        self.pubSubHandler.handlePublish("/App/Loaded")
