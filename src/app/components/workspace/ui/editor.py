from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import (
    QInputDialog,
    QLineEdit,
    QPushButton,
    QShortcut,
    QVBoxLayout,
    QWidget,
)

from src.app.components.workspace.model import WorkspaceModel
from src.app.state import Context

from .controller import WorkspaceController
from .view import WorkspaceView


class WorkspaceEditor(QWidget):
    requestWorkspace = pyqtSignal(str)

    def __init__(self, context: Context, model: WorkspaceModel):
        super().__init__()
        self.layout = QVBoxLayout(self)

        self.view = WorkspaceView(model)
        self.controller = WorkspaceController(context, self.view, model)

        self.shortcut = QShortcut(QKeySequence.New, self)
        self.shortcut.setContext(Qt.ApplicationShortcut)
        key = self.shortcut.key().toString(QKeySequence.NativeText)
        self.btn = QPushButton(f"Add Workspace ({key})")

        self.btn.clicked.connect(self.onWorkspaceCreate)
        self.shortcut.activated.connect(self.onWorkspaceCreate)

        self.layout.addWidget(self.btn)
        self.layout.addStretch()

    def onWorkspaceCreate(self):
        name, ok = QInputDialog.getText(
            None,
            "QInputDialog.getText()",
            "Workspace Name:",
            QLineEdit.Normal,
            "WS Name",
        )
        if not ok:
            return False

        if not name:
            return

        self.requestWorkspace.emit(name)
