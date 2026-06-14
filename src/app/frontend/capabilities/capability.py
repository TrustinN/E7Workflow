from src.app.frontend.state import Context

from .buttons import Buttons
from .graph import GraphCapability
from .runner import RunnerCapability
from .serialization import SerializationCapability
from .workspace import WorkspaceCapability


class ApplicationCapability:
    def __init__(self, context: Context):
        self.wksCapability = WorkspaceCapability(context)
        self.graphCapability = GraphCapability(context)
        self.runnerCapability = RunnerCapability(context)
        self.serialCapability = SerializationCapability()

        self.nodes = [
            self.wksCapability,
            self.graphCapability,
            self.runnerCapability,
            self.serialCapability,
        ]

        self.buttons = Buttons()

        self.buttons.workspaceBtn.clicked.connect(self.wksCapability.requestWorkspace)
        self.buttons.setE1Btn.clicked.connect(self.graphCapability.setE1)
        self.buttons.setE2Btn.clicked.connect(self.graphCapability.setE2)
        self.buttons.createEdgeBtn.clicked.connect(self.graphCapability.requestEdge)
        self.buttons.entryBtn.clicked.connect(self.runnerCapability.requestEntry)
        self.buttons.executeBtn.clicked.connect(self.runnerCapability.requestExecute)
        self.buttons.exportBtn.clicked.connect(self.serialCapability.handleExport)
        self.buttons.importBtn.clicked.connect(self.serialCapability.handleImport)
