from PyQt5.QtGui import QColor

from src.app.frontend.state import Context
from src.app.frontend.state.layouts.graph import Color
from src.app.frontend.widgets.utils.colors import Alpha, Colors, with_alpha

from .components import WorkspaceSchema
from .view import WorkspaceView


class WorkspaceController:
    def __init__(self, context: Context, view: WorkspaceView):
        self.context = context
        self.view = view

        self.context.selectionModel.selected_.connect(self.onSelection)

        self.view.workspacePressed_.connect(self.onWorkspacePressed)

    def setColor(self, id, color: QColor, borderColor: QColor):
        schema = WorkspaceSchema(
            color=Color(*color.getRgb()),
            borderColor=Color(*borderColor.getRgb()),
        )
        self.view.setData(id, schema)

    def onSelection(self, id):
        prevID = self.context.selectionModel.getPrevSelected()
        if prevID:
            color = Colors.DEFAULT_COLOR
            borderColor = Colors.DEFAULT_BORDER
            self.setColor(prevID, color, borderColor)

        if id:
            color = with_alpha(Colors.SKY_BLUE, Alpha.LIGHT)
            borderColor = with_alpha(Colors.SKY_BLUE, Alpha.MEDIUM)
            self.setColor(id, color, borderColor)

    def onWorkspacePressed(self, id):
        self.context.selectionModel.setSelected(id)

    def setIcon(self, id, iconPath):
        schema = WorkspaceSchema(iconPath=iconPath)
        self.view.setData(id, schema)

    def resetState(self):
        self.view.clearState()
