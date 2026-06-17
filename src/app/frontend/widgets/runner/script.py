from src.app.frontend.state import Context

from .components import EdgeEditor


class ScriptSync:
    def __init__(self, context: Context, editor: EdgeEditor):
        self.context = context
        self.editor = editor

        self.editor.editorUpdated.connect(self.onEditorUpdate)
        self.freeze = False

    def onEditorUpdate(self, id):
        if self.freeze:
            return

        data = self.editor.getData(id)

        self.context.codeModel.setData(id, {"name": data["name"], "code": data["code"]})

    def freezeState(self):
        self.freeze = True

    def unfreezeState(self):
        self.freeze = False

    def clearState(self):
        self.freeze = False
