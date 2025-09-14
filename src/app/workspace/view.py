from functools import partial

from PyQt5.QtCore import QObject, pyqtSignal

from .workspace import Workspace


class WorkspaceView(QObject):
    workspacePressed_ = pyqtSignal(str)

    def __init__(self):
        super().__init__()

        self.focusedWorkspace = None
        self.workspaces: dict[str, Workspace] = {}

    def createWorkspace(self, id, parentID):
        workspace = Workspace()
        workspace.show()
        workspace.unlock()
        self.workspaces[id] = workspace

        if parentID:
            self.workspaces[parentID].addChild(workspace)

        onWorkspacePressed = partial(self.onWorkspacePressed, id)
        workspace.mousePress.connect(onWorkspacePressed)

    def updateWorkspace(self, id, data):
        workspace = self.workspaces[id]
        workspace.setData(data)

    def onWorkspacePressed(self, id):
        self.focusedWorkspace = id
        self.workspacePressed_.emit(id)
