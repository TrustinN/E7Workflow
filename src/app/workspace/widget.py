from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QInputDialog, QLineEdit, QPushButton, QVBoxLayout, QWidget

from src.router.routing import Dispatcher, Endpoint, RequestType, route

from .controller import WorkspaceController
from .service import WORKSPACE_SERVICE, WorkspaceServiceRoute
from .view import WorkspaceView


class WorkspaceWidget(QWidget):
    workspaceCreated_ = pyqtSignal(str)
    workspacePressed_ = pyqtSignal(str)

    workspaceUpdated_ = pyqtSignal(str)

    def __init__(self, dispatcher: Dispatcher):
        super().__init__()

        self.endpoint = Endpoint("Workspace Widget", dispatcher)
        response = self.endpoint.send(
            {},
            RequestType.GET,
            route(WorkspaceServiceRoute.WORKSPACE),
            WORKSPACE_SERVICE,
        )
        model = response["treeModel"]
        view = WorkspaceView()
        view.workspacePressed_.connect(self.workspacePressed_.emit)
        self.controller = WorkspaceController(model, view)

    def createWorkspace(self, name=None):
        response = self.endpoint.send(
            {},
            RequestType.POST,
            route(WorkspaceServiceRoute.WORKSPACE),
            WORKSPACE_SERVICE,
        )
        id = response["workspaceID"]
        self.workspaceCreated_.emit(id)

        if not name:
            name, ok = QInputDialog.getText(
                self,
                "QInputDialog.getText()",
                "Workspace Name:",
                QLineEdit.Normal,
                "WS Name",
            )
        self.updateWorkspace(id, {"text": name})

    def updateWorkspace(self, id, data):
        self.endpoint.send(
            data,
            RequestType.PUT,
            route(WorkspaceServiceRoute.WORKSPACE, id),
            WORKSPACE_SERVICE,
        )

        self.workspaceUpdated_.emit(id)

    def focusedWorkspace(self):
        return self.controller.focusedWorkspace()

    def setFocusedWorkspace(self, id):
        self.controller.setFocusedWorkspace(id)
