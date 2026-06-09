from PyQt5.QtWidgets import QWidget

from src.app.frontend.state import WorkspaceContext
from src.router.routing import Dispatcher

from .node import RunnerNode


class RunnerComponent(QWidget):
    def __init__(self, context: WorkspaceContext, dispatcher: Dispatcher):
        super().__init__()

        self.context = context
        self.node = RunnerNode(self.context, dispatcher)
