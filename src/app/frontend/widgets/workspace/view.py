from functools import partial

from PyQt5.QtCore import QObject, pyqtSignal

from src.app.frontend.widgets.workspace.components import Workspace

from .components.windows.utils import layoutToBBox


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
        workspace.moveSignal.connect(onWorkspaceChanged)
        workspace.resizeSignal.connect(onWorkspaceChanged)

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

    def setName(self, id, name):
        workspace = self.workspaces[id]
        workspace.setName(name)

    def setPadding(self, id, padding):
        workspace = self.workspaces[id]
        workspace.setPadding(padding)

    def setIcon(self, id, svgPath):
        workspace = self.workspaces[id]
        workspace.setIcon(svgPath)

    def setData(self, id, data):
        workspace = self.workspaces[id]
        workspace.setData(data)

    def setColor(self, id, fill, border):
        self.workspaces[id].setColor(fill, border)

    def setGeometry(self, id, geometry):
        self.workspaces[id].setGeometry(layoutToBBox(geometry))

    def getGeometry(self, id):
        return self.workspaces[id].getGeometry()

    def restoreData(self, id, data):
        workspace = self.workspaces[id]
        workspace.setData(data)

    def getData(self, id):
        workspace = self.workspaces[id]
        return workspace.getData()

    def clearState(self):
        rootWorkspace = self.workspaces[self.rootID]
        rootWorkspace.deleteLater()

        self.workspaces.clear()
        self.rootID = None
