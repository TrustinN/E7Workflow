from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget

from src.app.frontend.components import Capability, Component, JsonFormatter

from ..widget import WorkspaceWidget
from .controller import WorkspaceController
from .repository import WorkspaceRepository
from .view import WorkspaceView


class WorkspaceUIComponent(Component):
    CREATE_WK = "Create Workspace"
    UPDATE_WK = "Update Workspace"

    GET_WK_NAME = "Get Workspace Name"

    def __init__(self, wkUI: "WorkspaceUI"):
        super().__init__()
        self.gui = wkUI

        createFormatter = JsonFormatter(["id", "parentID"])
        getNameFormatter = JsonFormatter(["text"])

        createWkCapability = Capability(self.createWk, reformat=createFormatter)
        updateWkCapability = Capability(self.updateWk)
        getWkNameCapability = Capability(self.getWkName, reformat=getNameFormatter)

        self.registerCapability(self.CREATE_WK, createWkCapability)
        self.registerCapability(self.UPDATE_WK, updateWkCapability)
        self.registerCapability(self.GET_WK_NAME, getWkNameCapability)

    def createWk(self, data):
        return self.gui.create()

    def updateWk(self, data):
        id = data.get("id")
        self.gui.update(id, data)

    def getWkName(self, data):
        return self.gui.reqWkName()


class WorkspaceUI(QWidget):
    workspacePressed_ = pyqtSignal(str)
    workspaceCreated_ = pyqtSignal()
    workspaceImport_ = pyqtSignal()
    workspaceExport_ = pyqtSignal()

    def __init__(self, widget: WorkspaceWidget, repository: WorkspaceRepository):
        super().__init__()
        self.view = WorkspaceView()
        self.controller = WorkspaceController(self.view)

        self.widget = widget
        self.repository = repository

        self.view.workspacePressed_.connect(self.workspacePressed_.emit)
        self.widget.createWorkspaceBtn.clicked.connect(self.workspaceCreated_.emit)
        self.widget.exportWorkspaceBtn.clicked.connect(self.workspaceExport_.emit)
        self.widget.restoreWorkspaceBtn.clicked.connect(self.workspaceImport_.emit)

    def create(self):
        parentID = self.view.focusedWorkspace
        id = self.repository.createWorkspace()
        self.controller.createWorkspace(id, parentID)

        return id, parentID

    def update(self, id, data):
        self.repository.updateWorkspace(id, data)
        self.controller.updateWorkspace(id, data)

    def reqWkName(self):
        return self.widget.getWorkspaceName()

    def clear(self):
        self.controller.clearState()
