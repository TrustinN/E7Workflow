from nanoid import generate
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QInputDialog, QLineEdit, QPushButton, QVBoxLayout, QWidget

from ..constants import ROOT_ID
from ..routing import Dispatcher, Endpoint, EndpointService, Packet, RequestType
from ..workspace.workspace import WORKSPACE_DEFAULT_BORDER, WORKSPACE_DEFAULT_COLOR
from .workspace import Workspace


class EditorActions(QWidget):
    add_ = pyqtSignal()
    delete_ = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()

        self.buttonLabels = [
            "Add",
            "Delete",
        ]
        self.buttons = [QPushButton(label) for label in self.buttonLabels]
        self.signals = [
            self.add_,
            self.delete_,
        ]

        for btn, sig in zip(self.buttons, self.signals):
            self.layout.addWidget(btn)
            btn.clicked.connect(sig.emit)

        self.setLayout(self.layout)


class WorkspaceEditor(QWidget):
    activeChanged_ = pyqtSignal(object, object)
    workspaceCreated_ = pyqtSignal(object, object)

    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.activeWorkspace_ = None
        self.workspaces: dict[str, Workspace] = {}

        self.actions = EditorActions()

        self.actions.add_.connect(self.createWorkspace)
        self.actions.delete_.connect(self.deleteWorkspace)

        self.layout.addWidget(self.actions)

    def initState(self):
        rootWks = self.createWorkspace(ROOT_ID, "Root")
        rootWks.show()
        rootWks.unlock()
        rootWks.setPadding(15)

        self.setActiveWorkspace(ROOT_ID)

    def workspace(self, id):
        return self.workspaces[id]

    def activeWorkspace(self):
        return self.activeWorkspace_

    def modifyWorkspace(self, data):
        id = data["id"]
        color = data.get("color", WORKSPACE_DEFAULT_COLOR)
        borderColor = data.get("borderColor", WORKSPACE_DEFAULT_BORDER)

        wks = self.workspace(id)
        wks.setColor(color, borderColor)

    def setActiveWorkspace(self, id):
        prevID = None
        if self.activeWorkspace_:
            prevID = self.activeWorkspace_.id
        self.activeWorkspace_ = self.workspace(id)

        self.activeChanged_.emit(prevID, id)

    def newWorkspace(self, id=None, name=None):
        if not name:
            name, ok = QInputDialog.getText(
                self,
                "QInputDialog.getText()",
                "Workspace Name:",
                QLineEdit.Normal,
                "WS Name",
            )

        wks = None
        if id:
            wks = Workspace(id)
        else:
            wks = Workspace(generate())

        if name:
            wks.setName(name)

        wks.show()
        wks.unlock()
        return wks

    def createWorkspace(self, id=None, name=None):
        wks = self.newWorkspace(id, name)

        self.workspaces[wks.id] = wks
        activeWks = self.activeWorkspace()
        if activeWks:
            activeWks.addChild(wks)

        wks.mousePress.connect(lambda: self.setActiveWorkspace(wks.id))

        self.workspaceCreated_.emit(wks.id, wks.name)
        return wks

    def deleteWorkspace(self):
        raise RuntimeError("Not Implemented")

    def deleteAllWorkspaces(self):
        rootWks = self.workspace(ROOT_ID)
        rootWks.deleteLater()
        self.workspaces.clear()
        self.activeWorkspace_ = None


WORKSPACE_SERVICE = "WORKSPACE SERVICE"


class WorkspaceService(EndpointService):
    def __init__(self, dispatcher: Dispatcher):
        super().__init__(WORKSPACE_SERVICE, dispatcher)

        self.editor = WorkspaceEditor()
        self.editor.workspaceCreated_.connect(self.onWorkspaceCreated)
        self.editor.activeChanged_.connect(self.onSelectionChanged)

    def onWorkspaceCreated(self, id, name):
        self.endpoint.send({"id": id, "name": name}, topic="Workspace Created")

    def onSelectionChanged(self, prevID, nextID):
        self.endpoint.send(
            {"prevID": prevID, "nextID": nextID}, topic="Workspace Changed"
        )

    def handleGetRequest(self, packet: Packet):
        data = packet.data
        sender = packet.sender

        id = data["id"]
        self.sendData(self.editor.workspace(id), receiver=sender)

    def handlePostRequest(self, packet: Packet):
        data = packet.data

        action = data["action"]
        match action:
            case "create":
                id = data.get("id")
                name = data.get("name")
                self.editor.createWorkspace(id, name)
            case "focus":
                id = data["id"]
                self.editor.setActiveWorkspace(id)
            case "delete":
                self.editor.deleteAllWorkspaces()
                self.editor.initState()
            case "modify":
                self.editor.modifyWorkspace(data)
