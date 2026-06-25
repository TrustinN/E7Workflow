from src.app.events import Node

from .context import Context


class ContextManager(Node):
    def __init__(self, context: Context):
        super().__init__()
        self.context = context

        self.subscribe("/App/Reset", self.contextReset)

    def contextReset(self, data):
        self.document.clear()
