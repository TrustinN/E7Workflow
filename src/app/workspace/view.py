from functools import partial

from PyQt5.QtCore import QObject, pyqtSignal

from .workspace import Workspace


class WorkspaceView(QObject):
    workspacePressed_ = pyqtSignal(str)

    def __init__(self):
        super().__init__()

        self.workspaces: dict[str, Workspace] = {}

    def createWorkspace(self, id):
        workspace = Workspace()
        workspace.show()
        workspace.unlock()
        self.workspaces[id] = workspace

        workspace.mousePress.connect(partial(self.workspacePressed_.emit, id))

    def updateWorkspace(self, id, data):
        workspace = self.workspaces[id]

        text = data.get("text")
        parentID = data.get("parentID")
        padding = data.get("padding")
        if text:
            workspace.setName(text)

        if parentID:
            parent = self.workspaces[parentID]
            parent.addChild(workspace)

        if padding:
            workspace.setPadding(padding)
