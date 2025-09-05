from PyQt5.QtWidgets import QInputDialog, QLineEdit, QPushButton, QVBoxLayout, QWidget

from src.router.routing import Dispatcher, Endpoint, RequestType, route

from .controller import WorkspaceController
from .service import WORKSPACE_SERVICE, WorkspaceServiceRoute
from .view import WorkspaceView


class WorkspaceWidget(QWidget):
    def __init__(self, dispatcher: Dispatcher):
        super().__init__()

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.endpoint = Endpoint("Workspace Widget", dispatcher)
        response = self.endpoint.send(
            {},
            RequestType.GET,
            route(WorkspaceServiceRoute.WORKSPACE),
            WORKSPACE_SERVICE,
        )
        model = response["treeModel"]
        view = WorkspaceView()
        self.controller = WorkspaceController(model, view)

        self.createWorkspaceBtn = QPushButton("Create Workspace")

        self.createWorkspaceBtn.clicked.connect(self.createWorkspace)

        self.layout.addWidget(self.createWorkspaceBtn)

    def createWorkspace(self):
        response = self.endpoint.send(
            {},
            RequestType.POST,
            route(WorkspaceServiceRoute.WORKSPACE),
            WORKSPACE_SERVICE,
        )
        id = response["workspaceID"]

        name, ok = QInputDialog.getText(
            self,
            "QInputDialog.getText()",
            "Workspace Name:",
            QLineEdit.Normal,
            "WS Name",
        )
        self.endpoint.send(
            {"text": name},
            RequestType.PUT,
            route(WorkspaceServiceRoute.WORKSPACE, id),
            WORKSPACE_SERVICE,
        )
