from PyQt5.QtWidgets import QApplication, QHBoxLayout, QMainWindow, QVBoxLayout, QWidget

from src.router.routing import Dispatcher

from .frontend.capabilities import ApplicationCapability
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

        self._initState()
        self._initCapabilities()
        self._initComponents(self.context, self.document, dispatcher)
        self._initLayout()

        self.pubSubHandler = PubSubHandler()
        self.pubSubHandler.registerNode(self.contextManager)
        self.pubSubHandler.registerNodes(self.capabilites.nodes)
        self.pubSubHandler.registerNodes(self.components)
        self.pubSubHandler.handlePublish("/App/Loaded")

    def _initState(self):
        self.context = Context()
        self.document = Document()
        self.contextManager = StateManager(self.context, self.document)

    def _initCapabilities(self):
        self.capabilites = ApplicationCapability(self.context)

    def _initComponents(self, context, document, dispatcher):
        self.wkCpt = WorkspaceComponent(context, document)
        self.graphCpt = GraphComponent(context, document)
        self.runnerCpt = RunnerComponent(context, document, dispatcher)

        self.components = [self.wkCpt, self.graphCpt, self.runnerCpt]

    def _initLayout(self):
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

        self.layoutLeft.addWidget(self.graphCpt.widget)
        self.layoutLeft.addStretch()
        self.layoutRight.addWidget(self.capabilites.buttons)
        self.layoutRight.addWidget(self.runnerCpt.widget)
        self.layoutRight.addStretch()
