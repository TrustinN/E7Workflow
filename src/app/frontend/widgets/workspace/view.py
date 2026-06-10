from functools import partial

from PyQt5.QtCore import QObject, pyqtSignal

from src.app.frontend.widgets.workspace.components import Workspace


class WorkspaceView(QObject):
    workspaceCreated_ = pyqtSignal(str)
    workspacePressed_ = pyqtSignal(str)
    workspaceUpdate_ = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.workspaces: dict[str, Workspace] = {}

    def setWorkspaceName(self, id, name):
        workspace = self.workspaces[id]
        workspace.setName(name)

    def setWorkspacePadding(self, id, padding):
        workspace = self.workspaces[id]
        workspace.setPadding(padding)

    def setWorkspaceIcon(self, id, svgPath):
        workspace = self.workspaces[id]
        workspace.setIcon(svgPath)

    def updateWorkspace(self, id, data):
        workspace = self.workspaces[id]
        workspace.setData(data)

    def _createWorkspace(self, id):
        workspace = Workspace()
        workspace.show()
        workspace.unlock()

        onWorkspacePressed = partial(self.workspacePressed_.emit, id)
        workspace.mousePress.connect(onWorkspacePressed)

        onWorkspaceUpdate = partial(self.workspaceUpdate_.emit, id)
        workspace.resizeSignal.connect(onWorkspaceUpdate)
        workspace.moveSignal.connect(onWorkspaceUpdate)

        self.workspaces[id] = workspace

        return workspace

    def createRootWorkspace(self, id):
        self._createWorkspace(id)
        self.workspaceCreated_.emit(id)

    def createChildWorkspace(self, id, parentID):
        workspace = self._createWorkspace(id)
        self.workspaces[parentID].addChild(workspace)
        self.workspaceCreated_.emit(id)

    def setWorkspaceColor(self, id, fill, border):
        self.workspaces[id].setColor(fill, border)

    def restoreWorkspaceData(self, id, data):
        workspace = self.workspaces[id]
        workspace.setData(data)

    def getWorkspaceData(self, id):
        workspace = self.workspaces[id]
        return workspace.getData()

    def clear(self, rootID):
        rootWorkspace = self.workspaces[rootID]
        rootWorkspace.deleteLater()

        self.workspaces.clear()
