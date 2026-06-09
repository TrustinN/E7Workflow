from PyQt5.QtWidgets import QApplication, QHBoxLayout, QMainWindow, QVBoxLayout, QWidget

from .frontend.capabilities import Buttons, GraphCapability, WorkspaceCapability
from .frontend.events import PubSubHandler
from .frontend.state import WorkspaceContext, WorkspaceContextManager

# from .frontend.widgets.runner import RunnerComponent
from .frontend.widgets.graph import GraphComponent
from .frontend.widgets.serialization import SerializationComponent
from .frontend.widgets.workspace import WorkspaceComponent


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

    def closeEvent(self, event):
        QApplication.quit()


class App(QApplication):
    def __init__(self):
        super().__init__([])

        self.window = MainWindow()
        self.widget = QWidget()

        self.layout = QHBoxLayout()
        self.layoutLeft = QVBoxLayout()
        self.layout.addLayout(self.layoutLeft)

        self.widget.setLayout(self.layout)
        self.window.setCentralWidget(self.widget)
        self.window.show()

        self.context = WorkspaceContext()
        self.contextManager = WorkspaceContextManager(self.context)

        self.buttons = Buttons()
        self.wksCapability = WorkspaceCapability()
        self.graphCapability = GraphCapability()

        self.buttons.createWorkspace_.connect(self.wksCapability.createWorkspace)
        self.buttons.createEdgeBtn.clicked.connect(self.graphCapability.createEdge)

        self.wkCpt = WorkspaceComponent(self.context)
        self.graphCpt = GraphComponent(self.context)
        self.serialCpt = SerializationComponent()

        self.layoutLeft.addWidget(self.buttons)
        self.layoutLeft.addWidget(self.serialCpt)
        self.layout.addWidget(self.graphCpt)

        self.pubSubHandler = PubSubHandler()
        self.pubSubHandler.registerNode(self.contextManager)

        self.pubSubHandler.registerNode(self.wksCapability)
        self.pubSubHandler.registerNode(self.graphCapability)

        self.pubSubHandler.registerNode(self.wkCpt.node)
        self.pubSubHandler.registerNode(self.graphCpt.node)
        self.pubSubHandler.registerNode(self.serialCpt.node)
        self.pubSubHandler.handlePublish("/App/Loaded")
