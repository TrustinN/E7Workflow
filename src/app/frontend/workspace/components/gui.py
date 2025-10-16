from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget

from src.app.frontend.components import Capability, Component
from src.app.frontend.events import EventLog

from ..events import WKEvents
from ..widget import WorkspaceWidget
from .controller import WorkspaceController
from .repository import WorkspaceRepository
from .view import WorkspaceView


class WorkspaceUIComponent(Component):
    CREATE_WK = "Create Workspace"
    UPDATE_WK = "Update Workspace"

    GET_WK_NAME = "Get Workspace Name"

    def __init__(self, wkUI: "WorkspaceUI", eventLog: EventLog):
        super().__init__()
        self.gui = wkUI
        self.eventLog = eventLog

        self.gui.wkPressed_.connect(self.focusedWk)

        createWkCapability = Capability(self.createWk)
        updateWkCapability = Capability(self.updateWk)
        getWkNameCapability = Capability(self.getWkName)

        self.registerCapability(self.CREATE_WK, createWkCapability)
        self.registerCapability(self.UPDATE_WK, updateWkCapability)
        self.registerCapability(self.GET_WK_NAME, getWkNameCapability)

    def createWk(self, data):
        id, parentID = self.gui.create()
        data.update({"wkID": id, "parentID": parentID})
        if parentID is None:
            self.eventLog.processEvent(WKEvents.WK_CREATED_ROOT, data)
        else:
            self.eventLog.processEvent(WKEvents.WK_CREATED, data)
        return data

    def updateWk(self, data):
        id = data.get("wkID")
        self.gui.update(id, data)
        self.eventLog.processEvent(WKEvents.WK_UPDATED, data)

    def getWkName(self, data):
        name = self.gui.reqWkName()
        data.update({"text": name})
        return data

    def focusedWk(self, id):
        self.eventLog.processEvent(WKEvents.WK_FOCUSED, {"wkID": id})


class WorkspaceUI(QWidget):
    wkPressed_ = pyqtSignal(str)
    wkCreated_ = pyqtSignal()
    wkImport_ = pyqtSignal()
    wkExport_ = pyqtSignal()

    def __init__(self, widget: WorkspaceWidget, repository: WorkspaceRepository):
        super().__init__()
        self.view = WorkspaceView()
        self.controller = WorkspaceController(self.view)

        self.widget = widget
        self.repository = repository

        self.view.wkPressed_.connect(self.wkPressed_.emit)
        self.widget.createBtn.clicked.connect(self.wkCreated_.emit)
        self.widget.exportBtn.clicked.connect(self.wkExport_.emit)
        self.widget.restoreBtn.clicked.connect(self.wkImport_.emit)

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
