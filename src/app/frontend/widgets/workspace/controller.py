import os

from src.app.config import ICON_DIR
from src.app.frontend.state import Context, Document
from src.app.frontend.state.layouts.graph import Color
from src.app.frontend.widgets.utils.colors import Alpha, Colors, with_alpha

from .components import WorkspaceSchema
from .view import WorkspaceView


class WorkspaceController:
    def __init__(self, context: Context, view: WorkspaceView):
        self.context = context
        self.view = view

        self.iconPaths = {
            "Click": os.path.join(ICON_DIR, "mouse-pointer-click.svg"),
            "Drag.down": os.path.join(ICON_DIR, "move-down.svg"),
            "Drag.left": os.path.join(ICON_DIR, "move-left.svg"),
            "Drag.right": os.path.join(ICON_DIR, "move-right.svg"),
            "Drag.up": os.path.join(ICON_DIR, "move-up.svg"),
        }

        self.context.actionModel.dataSet_.connect(self.onActionBind)
        self.context.actionModel.dataRemoved_.connect(self.onActionUnbind)

        self.context.selectionModel.selected_.connect(self.onSelection)

        self.view.workspacePressed_.connect(self.onWorkspacePressed)

    def onSelection(self, id):
        prevID = self.context.selectionModel.getPrevSelected()
        if prevID:
            color = Colors.DEFAULT_COLOR
            borderColor = Colors.DEFAULT_BORDER
            schema = WorkspaceSchema(
                color=Color(*color.getRgb()),
                borderColor=Color(*borderColor.getRgb()),
            )
            self.view.setData(prevID, schema)

        if id:
            color = with_alpha(Colors.SKY_BLUE, Alpha.LIGHT)
            borderColor = with_alpha(Colors.SKY_BLUE, Alpha.MEDIUM)
            schema = WorkspaceSchema(
                color=Color(*color.getRgb()),
                borderColor=Color(*borderColor.getRgb()),
            )
            self.view.setData(id, schema)

    def onWorkspacePressed(self, id):
        self.context.selectionModel.setSelected(id)

    def clearState(self):
        self.view.clearState()

    def getIconPath(self, data):
        name = data["name"]
        if name == "Click":
            return self.iconPaths[name]
        elif name == "Drag":
            userParams = data["userParams"]
            direction = userParams["dir"]["value"]
            return self.iconPaths[f"{name}.{direction}"]

    def onActionBind(self, id):
        data = self.context.actionModel.getData(id)
        self.view.setIcon(id, self.getIconPath(data))

    def onActionUnbind(self, id):
        self.view.setIcon(id, "")
