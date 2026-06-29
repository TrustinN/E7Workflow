import json
import os
from pathlib import Path

from nanoid import generate

from src.app.config import CUSTOM_SCRIPTS_DIR
from src.app.events import Node
from src.app.state import Context
from src.router.routing import Dispatcher

from .model import ScriptModel, ScriptSchema, ScriptViewModel
from .service import ScriptService
from .ui import ScriptEditorController, ScriptManager


class ScriptComponent(Node):
    def __init__(self, context: Context, dispatcher: Dispatcher):
        super().__init__()

        self.context = context

        self.model = ScriptModel()
        self.viewModel = ScriptViewModel()
        self.editor = ScriptManager()

        self.controller = ScriptEditorController(
            self.editor, self.model, self.viewModel
        )
        self.service = ScriptService(self.model, self.viewModel, dispatcher)

        self.subscribe("/App/Loaded", self.loadCustomScripts)
        self.subscribe("/App/Export", self.saveState)
        self.subscribe("/App/Reset", self.resetState)
        self.subscribe("/App/Import", self.loadState)

        self.model.scriptUpdated.connect(self.onScriptUpdate)

    def loadCustomScripts(self, data):
        p = Path(CUSTOM_SCRIPTS_DIR)
        for file in p.iterdir():

            if not file.is_file():
                continue

            content = file.read_text(encoding="utf-8")
            id = generate()
            self.model.addScript(
                id=id,
                schema=ScriptSchema(
                    name=file.stem,
                    code=content,
                ),
            )
            self.editor.addCodeTab(id, file.stem, content)

    def onScriptUpdate(self, id: str):
        schema = self.model.getScript(id)
        self.publish("/Script/Updated", {"id": id, "schema": schema.toData()})

    def saveState(self, data):
        path = data["path"]
        saveFile = os.path.join(path, "scripts.json")
        state = self.model.toData()
        with open(saveFile, "w") as f:
            json.dump(state, f, indent=4)

    def resetState(self, data):
        self.model.clear()

    def loadState(self, data):
        path = data["path"]
        saveFile = os.path.join(path, "scripts.json")
        state = None
        with open(saveFile, "r") as f:
            state = json.load(f)

        self.model.fromData(state)
