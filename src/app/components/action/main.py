import json
import os

from src.app.components.workspace.model import WorkspaceSchema
from src.app.events import Node
from src.app.state import Context, SelectionType

from .actions import ClickAction, DragAction
from .model import ActionModel, ActionSchema
from .ui import ActionEditor


class ActionComponent(Node):
    def __init__(self, context: Context):
        super().__init__()

        self.context = context

        self.editor = ActionEditor()
        self.editor.addAction(ClickAction.info())
        self.editor.addAction(DragAction.info())
        self.editor.requestSetAction.connect(self.setAction)

        self.model = ActionModel()

        self.subscribe("/Workspace/Created", self.unsetAction)
        self.subscribe("/App/Export", self.saveState)
        self.subscribe("/App/Reset", self.resetState)
        self.subscribe("/App/Import", self.loadState)

    def setAction(self):
        selection = self.context.selectionModel.getSelected()
        if not (selection.id and selection.type == SelectionType.WORKSPACE):
            return

        data = self.editor.getActionData()
        schema = ActionSchema.fromData(data)
        self.model.setAction(selection.id, schema)

    def unsetAction(self, data):
        schema = WorkspaceSchema.fromData(data)
        parentID = schema.parent
        self.model.unsetAction(parentID)

    def saveState(self, data):
        path = data["path"]
        saveFile = os.path.join(path, "actions.json")
        state = self.model.toData()
        with open(saveFile, "w") as f:
            json.dump(state, f, indent=4)

    def resetState(self, data):
        self.model.clear()

    def loadState(self, data):
        path = data["path"]
        saveFile = os.path.join(path, "actions.json")
        state = None
        with open(saveFile, "r") as f:
            state = json.load(f)

        self.model.fromData(state)
