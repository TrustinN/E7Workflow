from PyQt5.QtWidgets import QVBoxLayout, QWidget

from src.app.frontend.state import WorkspaceContext

from .components import WorkspaceButtons
from .node import WorkspaceNode
from .view import WorkspaceView


class WorkspaceComponent(QWidget):
    def __init__(self, context: WorkspaceContext):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.buttons = WorkspaceButtons()
        self.context = context

        self.node = WorkspaceNode(self.context)
        self.view = WorkspaceView(self.context)

        self.buttons.createWorkspace_.connect(self.node.createWorkspace)
        self.layout.addWidget(self.buttons)
