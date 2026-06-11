from functools import partial

from .models import GraphModel, MappingModel, Model, TreeModel
from .selection import SelectionModel


class WorkspaceContext(Model):

    def __init__(self):
        super().__init__()

        self.workspaceModel = TreeModel()
        self.graphModel = GraphModel()
        self.selectionModel = SelectionModel()

        self.actionModel = MappingModel()
        self.runnerModel = SelectionModel()

        self.models = {
            "tree": self.workspaceModel,
            "graph": self.graphModel,
            "selection": self.selectionModel,
            "action": self.actionModel,
            "runner": self.runnerModel,
        }

        self.loadedModels = set()

        for name, model in self.models.items():
            incrementLoaded = partial(self.incrementLoaded, name)
            model.modelLoaded_.connect(incrementLoaded)

    def incrementLoaded(self, name):
        self.loadedModels.add(name)

        if len(self.loadedModels) == len(self.models):
            self.modelLoaded_.emit()
            self.loadedModels.clear()

    def clear(self):
        self.workspaceModel.clear()
        self.graphModel.clear()
        self.selectionModel.clear()

        self.actionModel.clear()
        self.runnerModel.clear()

        self.modelClear_.emit()
