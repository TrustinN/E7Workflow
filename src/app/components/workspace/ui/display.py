from PyQt5.QtWidgets import QHeaderView, QTreeView

from src.app.state import Context, SelectionType

from .model import WorkspaceItemModel


class WorkspaceTreeView(QTreeView):
    def __init__(self, model: WorkspaceItemModel, context: Context):
        super().__init__()

        self.setModel(model)
        header = self.header()

        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Fixed)
        header.setSectionResizeMode(2, QHeaderView.Fixed)

        self.setColumnWidth(1, 60)
        self.setColumnWidth(2, 60)

        self.context = context
        self.selectionModel().selectionChanged.connect(self.onItemSelection)

    def onItemSelection(self, selected, deselected):
        indexes = selected.indexes()
        if not indexes:
            self.context.selectionModel.setSelected(None, SelectionType.NONE)
            return

        index = indexes[0]
        item = self.model().itemFromIndex(index)
        self.context.selectionModel.setSelected(item.id, SelectionType.WORKSPACE)
