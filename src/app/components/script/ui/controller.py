from nanoid import generate

from src.app.components.script.model import ScriptModel, ScriptSchema, ScriptViewModel

from .editor import ScriptManager


class ScriptEditorController:
    def __init__(
        self,
        editor: ScriptManager,
        model: ScriptModel,
        viewModel: ScriptViewModel,
    ):
        self.editor = editor
        self.model = model
        self.viewModel = viewModel

        self.editor.requestScript.connect(self.createScript)
        self.editor.editorUpdated.connect(self.updateScript)
        self.editor.editorSwitched.connect(self.setActiveScript)

        self.model.modelCleared.connect(self.editor.clear)
        self.model.modelLoaded.connect(self.loadEditor)

    def createScript(self):
        id = generate()
        name = self.model.uniqueName("Untitled")
        schema = ScriptSchema(name=name)
        self.model.addScript(id, schema)
        self.editor.addCodeTab(id, name)

    def updateScript(self, id):
        data = self.editor.getData(id)
        self.model.updateScript(id, data)

    def setActiveScript(self):
        id = self.editor.currentEditor()
        self.viewModel.setActiveScript(id)

    def loadEditor(self):
        for id in self.model.getScripts():
            schema = self.model.getScript(id)
            self.editor.setData(id, schema.toData())
