from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QInputDialog, QLineEdit, QWidget

from src.router.routing import Client, Dispatcher, Link

from .controller import WorkspaceController
from .service import ws
from .view import WorkspaceView


class WorkspaceWidget(QWidget):
    workspaceCreated_ = pyqtSignal(str)
    workspacePressed_ = pyqtSignal(str)

    workspaceUpdated_ = pyqtSignal(str)

    def __init__(self, dispatcher: Dispatcher):
        super().__init__()

        self.client = Client("Workspace Widget", dispatcher)
        self.view = WorkspaceView()
        self.view.workspacePressed_.connect(self.workspacePressed_.emit)
        self.controller = WorkspaceController(self.view)

    def createWorkspace(self, name=None):
        parentID = self.focusedWorkspace()

        response = self.client.post(Link(ws.NAME, ws.WORKSPACE), {"parentID": parentID})
        id = response["workspaceID"]
        if not name:
            name, ok = QInputDialog.getText(
                self,
                "QInputDialog.getText()",
                "Workspace Name:",
                QLineEdit.Normal,
                "WS Name",
            )

        self.view.createWorkspace(id, parentID)
        self.workspaceCreated_.emit(id)
        self.updateWorkspace(id, {"userData": {"text": name}})

    def updateWorkspace(self, id, data):
        self.client.put(Link(ws.NAME, ws.WORKSPACE, id), data)
        self.view.updateWorkspace(id, data["userData"])

        self.workspaceUpdated_.emit(id)

    def focusedWorkspace(self):
        return self.controller.focusedWorkspace()

    def setFocusedWorkspace(self, id):
        self.controller.setFocusedWorkspace(id)
