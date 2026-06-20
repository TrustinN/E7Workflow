from PyQt5.QtGui import QColor

from src.app.components.utils.colors import Alpha, Colors, with_alpha
from src.app.components.workspace.model import WorkspaceModel, WorkspaceSchema
from src.app.state import Context, Selection, SelectionType
from src.app.state.layouts.graph import Color

from .view import WorkspaceView


class WorkspaceController:
    def __init__(self, context: Context, view: WorkspaceView, model: WorkspaceModel):
        self.context = context
        self.view = view
        self.model = model

        self.context.selectionModel.selected_.connect(self.onSelection)

        self.view.workspacePressed.connect(self.onWorkspacePressed)
        self.view.workspaceUpdated.connect(self.setModelData)

    def setModelData(self, id):
        data = self.view.getData(id)
        self.model.updateItem(id, data)

    def setColor(self, id, color: QColor, borderColor: QColor):
        schema = WorkspaceSchema(
            color=Color(*color.getRgb()),
            borderColor=Color(*borderColor.getRgb()),
        )
        self.view.setData(id, schema)

    def onSelection(self, selection: Selection):
        prev: Selection = self.context.selectionModel.getPrevSelected()
        if prev.id and prev.type is SelectionType.WORKSPACE:
            self.setColor(prev.id, Colors.DEFAULT_COLOR, Colors.DEFAULT_BORDER)

        if selection.id and selection.type is SelectionType.WORKSPACE:
            color = with_alpha(Colors.SKY_BLUE, Alpha.LIGHT)
            borderColor = with_alpha(Colors.SKY_BLUE, Alpha.MEDIUM)
            self.setColor(selection.id, color, borderColor)

    def onWorkspacePressed(self, id):
        self.context.selectionModel.setSelected(id, SelectionType.WORKSPACE)

    def resetState(self):
        self.view.clearState()
