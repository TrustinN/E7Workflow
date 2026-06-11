import os

from src.app.frontend.events import Node

from .models import Serializer
from .workspace import WorkspaceContext


class WorkspaceContextManager(Node):
    def __init__(self, context: WorkspaceContext):
        super().__init__()
        self.context = context

        self.serializer = Serializer()

        self.treeFile = "workspace_data.json"
        self.graphFile = "graph_data.json"
        self.selectionFile = "selection_data.json"
        self.actionFile = "action_data.json"
        self.runnerFile = "runner_data.json"
        self.files = [
            self.treeFile,
            self.graphFile,
            self.selectionFile,
            self.actionFile,
            self.runnerFile,
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

        self.serializer.export(self.context.workspaceModel, paths[self.treeFile])
        self.serializer.export(self.context.graphModel, paths[self.graphFile])
        self.serializer.export(self.context.selectionModel, paths[self.selectionFile])
        self.serializer.export(self.context.actionModel, paths[self.actionFile])
        self.serializer.export(self.context.runnerModel, paths[self.runnerFile])

    def contextImport(self, data):
        path = data["path"]
        states = self.getStates(path)

        self.context.workspaceModel.deserialize(states[self.treeFile])
        self.context.graphModel.deserialize(states[self.graphFile])
        self.context.selectionModel.deserialize(states[self.selectionFile])
        self.context.actionModel.deserialize(states[self.actionFile])
        self.context.runnerModel.deserialize(states[self.runnerFile])

    def contextReset(self, data):
        self.context.clear()
