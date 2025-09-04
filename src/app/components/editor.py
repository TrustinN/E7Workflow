from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QComboBox, QVBoxLayout, QWidget

from ..components.data import WorkspaceData
from ..components.manager import WORKSPACE_MANAGER
from ..graph.editor import GraphService
from ..graph.graph import NodeState
from ..routing import Dispatcher, Endpoint, Packet
from ..workspace.editor import WorkspaceService

EDITOR = "Editor"


class EditorWidget(QWidget):
    dataReceived_ = pyqtSignal(object)

    workspaceCreated_ = pyqtSignal(object)
    edgeCreated_ = pyqtSignal(object)
    crossEdgeCreated_ = pyqtSignal(object)

    def __init__(self, dispatcher: Dispatcher):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        #
        # self.name = EDITOR
        # self.endpoint = Endpoint(self.name, dispatcher)
        # self.endpoint.addHandler(self.name, self.receiveData)

        self.workspaceService: WorkspaceService = WorkspaceService(dispatcher)
        self.graphService: GraphService = GraphService(dispatcher)

        # self.actions = QComboBox()

        # self.layout.addWidget(self.actions)
        self.layout.addWidget(self.workspaceService.editor)
        self.layout.addWidget(self.graphService.editor)
        self.workspaceService.editor.initState()
        #
        # self.data: WorkspaceData = None
        #
        # self.graphEditorActions.addEdge_.connect(self.addEdge)
        # self.graphEditorActions.addCrossEdge_.connect(lambda: self.onCrossEdgePress())
        #
        # self.graphEditor.edgeCreated_.connect(self.edgeCreated_)
        # self.graphEditor.crossEdgeCreated_.connect(self.crossEdgeCreated_)

    # def receiveData(self, packet: Packet):
    #     self.data = packet.data["data"]
    #
    # def getData(self, id=None):
    #     self.endpoint.send({"type": "GET", "id": id}, receiver=WORKSPACE_MANAGER)

    # def setActions(self, actions):
    #     for action in actions:
    #         self.actions.addItem(action)
    #
    # def addNode(self, scene, id, name=None):
    #     return self.graphEditor.addNode(scene, id, name)
    #
    # def addEdge(self):
    #     self.getData()
    #
    #     data = self.data
    #     self.graphEditor.addEdge(data.scene)
    #
