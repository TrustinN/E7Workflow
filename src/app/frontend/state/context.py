from .models import GraphModel, MappingModel, Model, TreeModel
from .selection import SelectionModel


class Context(Model):

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

    def clear(self):
        self.workspaceModel.clear()
        self.graphModel.clear()
        self.selectionModel.clear()

        self.actionModel.clear()
        self.runnerModel.clear()

        self.modelClear_.emit()

    def serialize(self):
        return {name: model.serialize() for name, model in self.models.items()}

    def deserialize(self, state):
        for name, data in state.items():
            self.models[name].deserialize(data)

        self.modelLoaded_.emit()
