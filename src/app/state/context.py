from .selection import SelectionModel


class Context:

    def __init__(self):
        self.selectionModel = SelectionModel()

        self.models = {
            "selection": self.selectionModel,
        }

    def clear(self):
        for model in self.models.values():
            model.clear()
