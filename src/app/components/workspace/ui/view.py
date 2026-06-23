from collections import deque
from functools import partial

from PyQt5.QtCore import QObject, pyqtSignal

from src.app.components.workspace.model import WorkspaceModel

from .windows import Workspace


class WorkspaceView(QObject):
    workspacePressed = pyqtSignal(str)
    workspaceUpdated = pyqtSignal(str)

    def __init__(self, model: WorkspaceModel):
        super().__init__()
        self.workspaces: dict[str, Workspace] = {}
        self.rootID = None
        self.model = model

        self.model.modelCreated.connect(self.handleModelCreate)
        self.model.modelUpdated.connect(self.handleModelUpdate)
        self.model.modelCleared.connect(self.clear)
        self.model.modelLoaded.connect(self.rebuild)

    def handleModelCreate(self, id):
        schema = self.model.getItem(id)
        parentID = schema.parent
        if parentID:
            self.createChildWorkspace(id, schema.parent)
        else:
            self.createRootWorkspace(id)
            self.rootID = id

        self.setData(id, schema.toData())

    def handleModelUpdate(self, id):
        schema = self.model.getItem(id)
        self.setData(id, schema.toData())

    def _createWorkspace(self, id):
        workspace = Workspace()
        workspace.show()
        workspace.unlock()

        emitPressed = partial(self.workspacePressed.emit, id)
        emitUpdated = partial(self.workspaceUpdated.emit, id)

        workspace.mousePress.connect(emitPressed)
        workspace.moveDone.connect(emitUpdated)
        workspace.resizeDone.connect(emitUpdated)

        self.workspaces[id] = workspace

        return workspace

    def createRootWorkspace(self, id):
        self._createWorkspace(id)

    def createChildWorkspace(self, id, parentID):
        workspace = self._createWorkspace(id)
        self.workspaces[parentID].addChild(workspace)

    def setData(self, id, data: dict):
        workspace = self.workspaces[id]
        workspace.setData(data)

    def getData(self, id) -> dict:
        workspace = self.workspaces[id]
        return workspace.getData()

    def clear(self):
        rootWorkspace = self.workspaces[self.rootID]
        rootWorkspace.deleteLater()

        self.workspaces.clear()

    def rebuild(self):
        self.rootID = self.model.rootIndex()

        queue = deque([self.rootID])
        while queue:
            cur = queue.popleft()
            schema = self.model.getItem(cur)
            if cur == self.rootID:
                self.createRootWorkspace(cur)
            else:
                self.createChildWorkspace(cur, schema.parent)

            self.setData(cur, schema.toData())

            for child in schema.children:
                queue.append(child)
