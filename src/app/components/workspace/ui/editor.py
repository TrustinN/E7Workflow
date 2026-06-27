from PyQt5.QtWidgets import (
    QInputDialog,
    QLineEdit,
    QPushButton,
    QShortcut,
    QVBoxLayout,
    QWidget,
)

from src.app.actions import ActionRegistry
from src.app.components.workspace.model import WorkspaceModel
from src.app.state import Context, SelectionType

from .controller import WorkspaceController
from .view import WorkspaceView


class WorkspaceEditor(QWidget):
    def __init__(
        self, context: Context, model: WorkspaceModel, actions: ActionRegistry
    ):
        super().__init__()
        self.layout = QVBoxLayout(self)

        self.context = context
        self.view = WorkspaceView(model)
        self.controller = WorkspaceController(context, self.view, model)

        action = actions.get("Create Workspace")
        self.createBtn = QPushButton(actions.displayText("Create Workspace"))
        self.createBtn.addAction(action)

        action = actions.get("Delete Workspace")
        self.deleteBtn = QPushButton(actions.displayText("Delete Workspace"))
        self.deleteBtn.addAction(action)

        self.layout.addWidget(self.createBtn)
        self.layout.addWidget(self.deleteBtn)
        self.layout.addStretch()

    def createWorkspace(self):
        selection = self.context.selectionModel.getSelected()
        if not (selection.id and selection.type is SelectionType.WORKSPACE):
            return selection.id, "", False

        name, ok = QInputDialog.getText(
            None,
            "QInputDialog.getText()",
            "Workspace Name:",
            QLineEdit.Normal,
            "WS Name",
        )
        if not (ok and name):
            return selection.id, name, False

        return selection.id, name, True
