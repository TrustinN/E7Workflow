import json
import os

from nanoid import generate

from src.app.events import Node
from src.app.state import Context

from .model import ScriptModel, ScriptSchema
from .ui import ScriptManager


class ScriptComponent(Node):
    def __init__(self, context: Context):
        super().__init__()

        self.context = context
        self.model = ScriptModel()

        self.editor = ScriptManager()
        self.editor.requestScript.connect(self.createScript)
        self.editor.editorUpdated.connect(self.updateScript)

        self.subscribe("/App/Export", self.saveState)
        self.subscribe("/App/Reset", self.resetState)
        self.subscribe("/App/Import", self.loadState)

    def createScript(self):
        id = generate()
        schema = ScriptSchema()
        self.model.addScript(id, schema)

        schema = self.model.getScript(id)
        self.editor.addCodeTab(id, schema.name)

    def updateScript(self, id):
        data = self.editor.getData(id)
        self.model.updateScript(id, data)

    def saveState(self, data):
        path = data["path"]
        saveFile = os.path.join(path, "scripts.json")
        state = self.model.toData()
        with open(saveFile, "w") as f:
            json.dump(state, f, indent=4)

    def resetState(self, data):
        self.model.clear()
        self.editor.clear()

    def loadState(self, data):
        path = data["path"]
        saveFile = os.path.join(path, "scripts.json")
        state = None
        with open(saveFile, "r") as f:
            state = json.load(f)

        self.model.fromData(state)

        for id in self.model.getScripts():
            schema = self.model.getScript(id)
            self.editor.setData(id, schema.toData())
