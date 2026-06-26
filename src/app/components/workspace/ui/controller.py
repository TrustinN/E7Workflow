from src.app.components.workspace.model import WorkspaceModel
from src.app.state import Context, Selection, SelectionType

from .view import WorkspaceView


class WorkspaceController:
    def __init__(self, context: Context, view: WorkspaceView, model: WorkspaceModel):
        self.context = context
        self.view = view
        self.model = model

        self.context.selectionModel.selected_.connect(self.onSelection)
        self.model.modelDeleted.connect(self.onWorkspaceDelete)

        self.view.workspacePressed.connect(self.onWorkspacePressed)
        self.view.workspaceUpdated.connect(self.setModelData)

    def setModelData(self, id):
        data = self.view.getData(id)
        self.model.updateItem(id, data)

    def onSelection(self, selection: Selection):
        if selection.type is SelectionType.WORKSPACE:
            self.view.setSelected(selection.id)
        else:
            self.view.removeSelection()

    def onWorkspacePressed(self, id):
        self.context.selectionModel.setSelected(id, SelectionType.WORKSPACE)

    def onWorkspaceDelete(self, id):
        self.context.selectionModel.onItemDelete(id, SelectionType.WORKSPACE)
