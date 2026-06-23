import os

from src.app.events import Node

from .context import Context
from .models import Serializer


class StateManager(Node):
    def __init__(self, context: Context):
        super().__init__()
        self.context = context

        self.serializer = Serializer()

        self.contextFile = "context.json"
        self.files = [
            self.contextFile,
        ]

        self.subscribe("/App/Reset", self.contextReset)
        self.subscribe("/App/Export", self.contextExport)
        self.subscribe("/App/Import", self.contextImport)

    def getPaths(self, path):
        return {file: os.path.join(path, file) for file in self.files}

    def getStates(self, path):
        paths = self.getPaths(path)
        return {file: self.serializer.restore(path) for file, path in paths.items()}

    def contextExport(self, data):
        path = data["path"]
        paths = self.getPaths(path)

        self.serializer.export(self.context, paths[self.contextFile])

    def contextImport(self, data):
        path = data["path"]
        states = self.getStates(path)

        self.context.deserialize(states[self.contextFile])

    def contextReset(self, data):
        self.document.clear()
