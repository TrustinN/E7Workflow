from .models import GraphModel, MappingModel, TreeModel
from .selection import SelectionModel


class WorkspaceContext:
    def __init__(self):
        self.wsGraphModel = GraphModel()
        self.wsTreeModel = TreeModel()
        self.viewModel = TreeModel()
        self.selectionModel = SelectionModel()

        self.actionModel = MappingModel()
