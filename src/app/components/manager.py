from PyQt5.QtCore import QObject, pyqtSignal

from ..graph.editor import InteractiveGraphScene
from ..routing import Dispatcher, Endpoint, Packet
from ..workspace.helpers import actions
from ..workspace.workspace import WORKSPACE_DEFAULT_COLOR, Workspace
from .data import WorkspaceData

WORKSPACE_MANAGER = "Workspace Manager"


class WorkspaceManager(QObject):
    workspaceRegistered = pyqtSignal(object)
    activeChanged = pyqtSignal(object)
    dataUpdate = pyqtSignal()

    def __init__(self, dispatcher: Dispatcher):
        super().__init__()
        self.name = WORKSPACE_MANAGER
        self.endpoint = Endpoint(self.name, dispatcher)
        self.endpoint.addHandler(f"{self.name}", self.receiveData)

    def setAction(self, wksID, action):
        data = self.data(wksID)
        data.action = actions[action]["func"]
        self.dataUpdate.emit()

    def sendData(self, data, receiver=None, topic=None):
        self.endpoint.send({"data": data}, receiver, topic)

    def receiveData(self, packet: Packet):
        data = packet.data

        type_ = data["type"]
        match type_:
            case "GET":
                self.handleGetRequest(packet)

    def handleGetRequest(self, packet):
        data = packet.data
        sender = packet.sender

        id = data["id"]
        self.sendData(self.data(id), receiver=sender)
