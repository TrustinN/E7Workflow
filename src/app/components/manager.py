from PyQt5.QtCore import QObject, pyqtSignal

from ..constants import ROOT_ID
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
        self.activeData = None
        self.dataHandler: dict[any, WorkspaceData] = {}

    def initState(self):
        rootWks = Workspace(ROOT_ID, "Root")
        rootWks.show()
        rootWks.unlock()
        rootWks.setPadding(15)

        self.registerWorkspace(rootWks)

    def reset(self):
        rootWks = self.workspace(ROOT_ID)
        rootWks.deleteLater()

        self.dataHandler.clear()
        self.activeData = None

    def registerWorkspace(self, wks: Workspace):
        wks.mousePress.connect(lambda: self.setActiveWorkspace(id))

        id = wks.id
        data = WorkspaceData()
        scene = InteractiveGraphScene()

        data.workspace = wks
        data.scene = scene

        scene.nodeSelected_.connect(
            lambda prevId: self.workspace(prevId).setColor(WORKSPACE_DEFAULT_COLOR)
        )

        self.dataHandler[id] = data

        if id == ROOT_ID:
            self.setActiveWorkspace(ROOT_ID)

        activeWks = self.workspace()
        if id != ROOT_ID:
            activeWks.addChild(wks)
            self.data().childData.append(data)
            data.parentData = self.data()
            self.workspaceRegistered.emit(id)

            data.node = self.scene().node(id)
            data.edges = self.scene().tuples[id]
            self.setAction(id, "none")

    def setActiveWorkspace(self, id):
        if self.scene():
            self.scene().setActiveNode(None)

        self.activeData = self.data(id)
        self.activeChanged.emit(id)

    def setAction(self, wksID, action):
        data = self.data(wksID)
        data.action = actions[action]["func"]
        self.dataUpdate.emit()

    def parentID(self, id):
        if id == ROOT_ID:
            return id

        return self.workspace(id).parentID

    def workspace(self, id=None) -> Workspace:
        data = self.data(id)
        if data:
            return self.data(id).workspace
        return None

    def scene(self, id=None) -> InteractiveGraphScene:
        data = self.data(id)
        if data:
            return self.data(id).scene

        return None

    def data(self, id=None) -> WorkspaceData:
        if id:
            return self.dataHandler[id]
        else:
            return self.activeData

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
