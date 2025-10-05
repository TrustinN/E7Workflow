from functools import partial

from PyQt5.QtCore import QObject, pyqtSignal

from .workspace import Workspace


class WorkspaceView(QObject):
    workspacePressed_ = pyqtSignal(str)

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
            self.onWorkspacePressed(id)
            self.rootID = id

    def readWorkspace(self, id):
        return self.workspaces[id].getData()

    def updateWorkspace(self, id, data):
        workspace = self.workspaces[id]
        workspace.setData(data)

    def onWorkspacePressed(self, id):
        self.focusedWorkspace = id
        self.workspacePressed_.emit(id)

    def clearState(self):
        self.focusedWorkspace = None
        rootWorkspace = self.workspaces[self.rootID]
        rootWorkspace.deleteLater()

        self.workspaces.clear()
        self.rootID = None


class WorkspaceController:
    def __init__(self):
        pass

    def setView(self, view: WorkspaceView):
        self.view = view

    def clearState(self):
        if self.view:
            self.view.clearState()

    def createWorkspace(self, id, parentID=None):
        self.view.createWorkspace(id, parentID)

    def readWorkspace(self, id):
        return self.view.readWorkspace(id)

    def updateWorkspace(self, id, data):
        self.view.updateWorkspace(id, data)
