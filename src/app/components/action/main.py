from src.app.components.workspace.model import WorkspaceSchema
from src.app.events import Node

from .actions import ClickAction, DragAction
from .ui import ActionEditor


class ActionComponent(Node):
    def __init__(self):
        super().__init__()

        self.editor = ActionEditor()

        self.editor.addAction(ClickAction.info())
        self.editor.addAction(DragAction.info())

        self.editor.requestSetAction.connect(self.setAction)

        self.subscribe("/Workspace/Created", self.unsetAction)

    def setAction(self):
        self.actionEditor.getActionData()

    # def requestActionSet(self):
    #     data = self.actionEditor.getActionData()
    #     self.publish("/Runner/Action/Set/Requested", data)
    #
    def unsetAction(self, data):
        schema = WorkspaceSchema.fromData(data)
        parentID = schema.parent
        return parentID
