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
        self.root: Workspace = None
        self.selected = None
        self.prevSelected = None
        self.model = model

        self.model.modelCreated.connect(self.handleModelCreate)
        self.model.modelUpdated.connect(self.handleModelUpdate)
        self.model.modelCleared.connect(self.clear)
        self.model.modelLoaded.connect(self.rebuild)

        self.workspacePressed.connect(self.setSelected)

    def handleModelCreate(self, id):
        schema = self.model.getItem(id)
        parentID = schema.parent
        if parentID:
            self.createChildWorkspace(id, schema.parent)
        else:
            self.root = self.createRootWorkspace(id)

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
        return self._createWorkspace(id)

    def createChildWorkspace(self, id, parentID):
        workspace = self._createWorkspace(id)
        self.workspaces[parentID].addChild(workspace)

    def setSelected(self, id):
        self.prevSelected = self.selected
        self.selected = id

        if self.prevSelected:
            self.workspaces[self.prevSelected].setSelected(False)

        self.workspaces[self.selected].setSelected(True)

    def removeSelection(self):
        self.prevSelected = self.selected
        self.selected = None

        if self.prevSelected:
            self.workspaces[self.prevSelected].setSelected(False)

    def setData(self, id, data: dict):
        workspace = self.workspaces[id]
        workspace.setData(data)

    def getData(self, id) -> dict:
        workspace = self.workspaces[id]
        return workspace.getData()

    def clear(self):
        self.root.deleteLater()

        self.root = None
        self.selected = None
        self.prevSelected = None

        self.workspaces.clear()

    def rebuild(self):
        rootID = self.model.rootIndex()

        queue = deque([rootID])
        while queue:
            cur = queue.popleft()
            schema = self.model.getItem(cur)
            if cur == rootID:
                self.root = self.createRootWorkspace(cur)
            else:
                self.createChildWorkspace(cur, schema.parent)

            self.setData(cur, schema.toData())

            for child in schema.children:
                queue.append(child)
