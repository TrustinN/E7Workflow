import json
import os

from src.app.events import Node
from src.app.state import Context
from src.router.routing import Dispatcher

from .actions import ClickAction, DragAction
from .model import ActionModel, ActionSchema
from .service import ActionService
from .ui import ActionEditor


class ActionComponent(Node):
    def __init__(self, context: Context, dispatcher: Dispatcher):
        super().__init__()

        self.context = context

        self.editor = ActionEditor()
        self.editor.actionChanged.connect(self.onActionChanged)

        self.model = ActionModel()

        self.subscribe("/App/Export", self.saveState)
        self.subscribe("/App/Reset", self.resetState)
        self.subscribe("/App/Import", self.loadState)

        self.editor.addAction(ClickAction.info())
        self.editor.addAction(DragAction.info())

        self.service = ActionService(self.model, dispatcher)

    def onActionChanged(self):
        data = self.editor.getActionData()
        schema = ActionSchema.fromData(data)
        self.model.setActiveAction(schema)

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
