from PyQt5.QtCore import QObject, pyqtSignal

from .controller import WorkspaceController
from .view import WorkspaceView


class WorkspaceMV(QObject):
    wkPressed_ = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.view = WorkspaceView()
        self.controller = WorkspaceController(self.view)

        self.view.wkPressed_.connect(self.wkPressed_.emit)

    def create(self, wkID):
        parentID = self.view.focusedWorkspace
        self.controller.createWorkspace(wkID, parentID)

        return parentID

    def update(self, id, data):
        self.controller.updateWorkspace(id, data)

    def clear(self):
        self.controller.clearState()
