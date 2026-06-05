from functools import partial

from PyQt5.QtCore import QObject, pyqtSignal

from .workspace import Workspace


class WorkspaceView(QObject):
    wkPressed_ = pyqtSignal(str)

    def __init__(self):
        super().__init__()

        self.rootID = None
        self.focusedWorkspace = None
        self.workspaces: dict[str, Workspace] = {}

    def createWorkspace(self, id, parentID=None):
        workspace = Workspace()
        workspace.show()
        workspace.unlock()

        onWorkspacePressed = partial(self.onWorkspacePressed, id)
        workspace.mousePress.connect(onWorkspacePressed)

        self.workspaces[id] = workspace

        parentID = self.focusedWorkspace
        if parentID:
            self.workspaces[parentID].addChild(workspace)
        else:
            self.focusedWorkspace = id
            self.rootID = id

    def readWorkspace(self, id):
        return self.workspaces[id].getData()

    def allWorkspaces(self):
        return list(self.workspaces.keys())

    def updateWorkspace(self, id, data):
        workspace = self.workspaces[id]
        workspace.setData(data)

    def onWorkspacePressed(self, id):
        self.focusedWorkspace = id
        self.wkPressed_.emit(id)

    def clearState(self):
        self.focusedWorkspace = None
        rootWorkspace = self.workspaces[self.rootID]
        rootWorkspace.deleteLater()

        self.workspaces.clear()
        self.rootID = None
