from .models import GraphModel, TreeModel
from .selection import SelectionModel


class WorkspaceContext:
    def __init__(self):
        self.wsGraphModel = GraphModel()
        self.wsTreeModel = TreeModel()
        self.viewModel = TreeModel()
        self.selectionModel = SelectionModel()
