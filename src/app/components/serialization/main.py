import os

from src.app.events import Node

from .ui import SerializerEditor


class SerializerComponent(Node):
    def __init__(self):
        super().__init__()

        self.editor = SerializerEditor()
        self.editor.exportRequested.connect(self.handleExport)
        self.editor.importRequested.connect(self.handleImport)

    def requestReset(self):
        self.publish("/App/Reset")

    def handleExport(self, path):
        os.makedirs(path, exist_ok=True)
        self.publish("/App/Export", {"path": path})

    def handleImport(self, path):
        self.requestReset()

        self.publish("/App/Import", {"path": path})
