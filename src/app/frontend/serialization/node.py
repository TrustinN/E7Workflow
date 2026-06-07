import os

from src.app.config import SAVE_DIR
from src.app.frontend.events import Node


class SerializationNode(Node):
    def __init__(self):
        super().__init__()

    def requestReset(self):
        self.publish("/App/Reset")

    def requestExport(self, id):
        path = os.path.join(SAVE_DIR, id)
        os.makedirs(path, exist_ok=True)
        self.publish("/App/Export", {"path": path})

    def requestImport(self, id):
        path = os.path.join(SAVE_DIR, id)
        self.publish("/App/Import", {"path": path})
