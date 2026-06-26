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
    requestCreate = pyqtSignal(str)
    requestDelete = pyqtSignal()

    def __init__(self, context: Context, model: WorkspaceModel):
        super().__init__()
        self.layout = QVBoxLayout(self)

        self.view = WorkspaceView(model)
        self.controller = WorkspaceController(context, self.view, model)

        self.createShortcut = QShortcut(QKeySequence.New, self)
        self.createShortcut.setContext(Qt.ApplicationShortcut)
        key = self.createShortcut.key().toString(QKeySequence.NativeText)
        self.createBtn = QPushButton(f"Add Workspace ({key})")
        self.createBtn.clicked.connect(self.onWorkspaceCreate)
        self.createShortcut.activated.connect(self.onWorkspaceCreate)

        self.deleteShortcut = QShortcut(QKeySequence("Meta+Backspace"), self)
        self.deleteShortcut.setContext(Qt.ApplicationShortcut)
        key = self.deleteShortcut.key().toString(QKeySequence.NativeText)
        self.deleteBtn = QPushButton(f"Delete Workspace ({key})")
        self.deleteBtn.clicked.connect(self.requestDelete.emit)
        self.deleteShortcut.activated.connect(self.requestDelete.emit)

        self.layout.addWidget(self.createBtn)
        self.layout.addWidget(self.deleteBtn)
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

        self.requestCreate.emit(name)
