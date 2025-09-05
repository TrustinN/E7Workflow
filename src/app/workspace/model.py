from dataclasses import dataclass, field
from functools import partial
from typing import Optional

from PyQt5.QtCore import QObject, QRect, pyqtSignal


@dataclass
class WorkspaceData:
    padding: Optional[int] = None
    parentID: Optional[str] = None
    text: Optional[str] = None
    geometry: QRect = field(default_factory=lambda: QRect(0, 0, 1, 1))
    children: list[str] = field(default_factory=list)


class WorkspaceModel(QObject):
    dataChanged_ = pyqtSignal()

    def __init__(self, data: WorkspaceData = None):
        super().__init__()

        if data:
            self.data = data
        else:
            self.data: WorkspaceData = WorkspaceData()

    def update(self, data: WorkspaceData):
        if data.text is not None:
            self.data.text = data.text

        if data.parentID is not None:
            self.data.parentID = data.parentID

        if data.padding is not None:
            self.data.padding = data.padding

        if len(data.children) != 0:
            self.data.children = data.children

        self.dataChanged_.emit()


class WorkspaceTreeModel(QObject):
    workspaceCreated_ = pyqtSignal(str, WorkspaceData)
    workspaceUpdated_ = pyqtSignal(str, WorkspaceData)

    workspaceFocused_ = pyqtSignal(str)

    def __init__(self):
        super().__init__()

        self.models: dict[str, WorkspaceModel] = {}
        self.focusedWorkspace: str = None

    def createWorkspace(self, id):
        model = WorkspaceModel()
        self.models[id] = model

        onWorkspaceChanged = partial(self.workspaceUpdated_.emit, id, model.data)
        model.dataChanged_.connect(onWorkspaceChanged)

        self.workspaceCreated_.emit(id, model.data)

    def updateWorkspace(self, id, data: WorkspaceData):
        workspaceModel = self.models[id]
        workspaceModel.update(data)

    def setFocusedWorkspace(self, id):
        self.focusedWorkspace = id
        self.workspaceFocused_.emit(id)
