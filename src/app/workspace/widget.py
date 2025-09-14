from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QInputDialog, QLineEdit, QWidget

from .view import WorkspaceView


class WorkspaceWidget(QWidget):
    workspaceCreated_ = pyqtSignal(str)
    workspaceUpdated_ = pyqtSignal(str)
    workspaceFocused_ = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.view = WorkspaceView()
        self.view.workspacePressed_.connect(self.workspaceFocused_.emit)

    def createWorkspace(self, id, parentID=None, name=None):
        if not name:
            name, ok = QInputDialog.getText(
                self,
                "QInputDialog.getText()",
                "Workspace Name:",
                QLineEdit.Normal,
                "WS Name",
            )

        self.view.createWorkspace(id, parentID)
        self.workspaceCreated_.emit(id)

    def updateWorkspace(self, id, data):
        self.view.updateWorkspace(id, data)
        self.workspaceUpdated_.emit(id)

    def focusedWorkspace(self):
        return self.view.focusedWorkspace

    def setFocusedWorkspace(self, id):
        self.view.focusedWorkspace = id
