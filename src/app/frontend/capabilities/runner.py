from src.app.frontend.events import Node


class RunnerCapability(Node):
    def __init__(self):
        super().__init__()

    def requestEntry(self):
        self.publish("/Runner/EntryRequested")

    def requestExecute(self):
        self.publish("/Runner/ExecuteRequested")
