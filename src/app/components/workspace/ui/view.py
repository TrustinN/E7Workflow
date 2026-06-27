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
        self.model.modelDeleted.connect(self.handleModelDelete)
        self.model.modelCleared.connect(self.clear)
        self.model.modelLoaded.connect(self.rebuild)

        self.workspacePressed.connect(self.setSelected)

    def handleModelCreate(self, id):
        schema = self.model.getItem(id)
        parentID = schema.parent
        data = schema.toData()
        if parentID:
            self.createChildWorkspace(id, schema.parent, data)
        else:
            self.root = self.createRootWorkspace(id, data)

    def handleModelUpdate(self, id):
        schema = self.model.getItem(id)
        self.setData(id, schema.toData())

    def handleModelDelete(self, id):
        wks = self.workspaces[id]
        wks.deleteLater()
        self.workspaces.pop(id)

        if id == self.selected:
            self.selected = None

        if id == self.prevSelected:
            self.prevSelected = None

    def _createWorkspace(self, id, data):
        workspace = Workspace()
        workspace.show()
        workspace.unlock()

        emitPressed = partial(self.workspacePressed.emit, id)
        emitUpdated = partial(self.workspaceUpdated.emit, id)

        workspace.mousePress.connect(emitPressed)
        workspace.moveDone.connect(emitUpdated)
        workspace.resizeDone.connect(emitUpdated)
        workspace.childAdded.connect(emitUpdated)

        self.workspaces[id] = workspace
        workspace.setData(data)

        return workspace

    def createRootWorkspace(self, id, data):
        return self._createWorkspace(id, data)

    def createChildWorkspace(self, id, parentID, data):
        workspace = self._createWorkspace(id, data)
        self.workspaces[parentID].addChild(id, workspace)

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
            data = schema.toData()
            if cur == rootID:
                self.root = self.createRootWorkspace(cur, data)
            else:
                self.createChildWorkspace(cur, schema.parent, data)

            for child in schema.children:
                queue.append(child)
