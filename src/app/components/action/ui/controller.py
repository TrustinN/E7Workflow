from src.app.components.action.actions import CaptureAction, ClickAction, DragAction
from src.app.components.action.model import ActionModel, ActionSchema, ActionViewModel

from .editor import ActionEditor


class ActionEditorController:
    def __init__(
        self,
        editor: ActionEditor,
        model: ActionModel,
        viewModel: ActionViewModel,
    ):

        self.editor = editor
        self.model = model
        self.viewModel = viewModel

        self.editor.actionChanged.connect(self.onActionChanged)

        self.editor.addAction(ClickAction.info())
        self.editor.addAction(DragAction.info())
        self.editor.addAction(CaptureAction.info())

    def onActionChanged(self):
        data = self.editor.getActionData()
        schema = ActionSchema.fromData(data)
        self.viewModel.setDraft(schema)
