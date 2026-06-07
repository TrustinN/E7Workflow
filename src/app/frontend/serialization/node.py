from src.app.frontend.events import Node


class SerializationNode(Node):
    def __init__(self):
        super().__init__()

    def requestReset(self):
        self.publish("/App/Reset")

    def requestExport(self):
        self.publish("/App/Export")

    def requestImport(self):
        self.publish("/App/Import")
