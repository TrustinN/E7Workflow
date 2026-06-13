from functools import partial

from PyQt5.QtCore import QObject, pyqtSignal

from src.app.frontend.widgets.workspace.components import Workspace, WorkspaceSchema


class WorkspaceView(QObject):
    workspaceCreated_ = pyqtSignal(str)
    workspacePressed_ = pyqtSignal(str)
    workspaceChanged_ = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.workspaces: dict[str, Workspace] = {}
        self.rootID = None

    def _createWorkspace(self, id):
        workspace = Workspace()
        workspace.show()
        workspace.unlock()

        onWorkspacePressed = partial(self.workspacePressed_.emit, id)
        onWorkspaceChanged = partial(self.workspaceChanged_.emit, id)

        workspace.mousePress.connect(onWorkspacePressed)
        workspace.moveDone.connect(onWorkspaceChanged)
        workspace.resizeDone.connect(onWorkspaceChanged)

        self.workspaces[id] = workspace

        return workspace

    def createRootWorkspace(self, id):
        self._createWorkspace(id)
        self.rootID = id
        self.workspaceCreated_.emit(id)

    def createChildWorkspace(self, id, parentID):
        workspace = self._createWorkspace(id)
        self.workspaces[parentID].addChild(workspace)
        self.workspaceCreated_.emit(id)

    def setData(self, id, data: WorkspaceSchema):
        workspace = self.workspaces[id]
        workspace.setData(data)
        self.workspaceChanged_.emit(id)

    def getData(self, id) -> WorkspaceSchema:
        workspace = self.workspaces[id]
        return workspace.getData()

    def clearState(self):
        rootWorkspace = self.workspaces[self.rootID]
        rootWorkspace.deleteLater()

        self.workspaces.clear()
        self.rootID = None
