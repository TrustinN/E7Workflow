from src.app.frontend.state import WorkspaceContext

from .controller import WorkspaceController
from .node import WorkspaceNode
from .view import WorkspaceView


class WorkspaceComponent:
    def __init__(self, context: WorkspaceContext):
        super().__init__()

        self.context = context

        self.view = WorkspaceView()
        self.controller = WorkspaceController(self.context, self.view)
        self.node = WorkspaceNode(self.context)
