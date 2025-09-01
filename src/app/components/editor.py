from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QComboBox, QGraphicsView, QVBoxLayout, QWidget

from ..components.data import WorkspaceData
from ..components.manager import WORKSPACE_MANAGER
from ..graph.editor import GraphEditor, GraphEditorActions
from ..graph.graph import NodeState
from ..routing import Dispatcher, Endpoint, Packet
from ..workspace.editor import WorkspacEditorActions, WorkspaceEditor

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

        self.name = EDITOR
        self.endpoint = Endpoint(self.name, dispatcher)
        self.endpoint.addHandler(self.name, self.receiveData)

        self.wksEditor: WorkspaceEditor = WorkspaceEditor()
        self.wksEditorActions: WorkspacEditorActions = WorkspacEditorActions()

        self.graphEditor: GraphEditor = GraphEditor()
        self.graphEditorActions: GraphEditorActions = GraphEditorActions()

        self.graphView = QGraphicsView()
        self.graphView.setFixedSize(400, 300)
        self.graphView.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.graphView.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.actions = QComboBox()

        self.layout.addWidget(self.actions)
        self.layout.addWidget(self.wksEditorActions)
        self.layout.addWidget(self.graphEditorActions)
        self.layout.addWidget(self.graphView)

        self.data: WorkspaceData = None

        self.wksEditorActions.add_.connect(self.addWorkspace)
        self.graphEditorActions.addEdge_.connect(self.addEdge)
        self.graphEditorActions.addCrossEdge_.connect(lambda: self.onCrossEdgePress())

        self.graphEditor.edgeCreated_.connect(self.edgeCreated_)
        self.graphEditor.crossEdgeCreated_.connect(self.crossEdgeCreated_)

    def receiveData(self, packet: Packet):
        self.data = packet.data["data"]

    def getData(self, id=None):
        self.endpoint.send({"type": "GET", "id": id}, receiver=WORKSPACE_MANAGER)

    def setActions(self, actions):
        for action in actions:
            self.actions.addItem(action)

    def addWorkspace(self, id=None, name=None):
        wks = self.wksEditor.addWorkspace(id, name)
        self.workspaceCreated_.emit(wks)

    def addNode(self, scene, id, name=None):
        return self.graphEditor.addNode(scene, id, name)

    def addEdge(self):
        self.getData()

        data = self.data
        self.graphEditor.addEdge(data.scene)

    def onCrossEdgePress(self, scene=None, id=None):
        self.getData()

        data = self.data
        if scene:
            scene2 = data.scene
            activeNode = scene2.activeNode()
            if activeNode:
                scene.node(id).setState(NodeState.DEFAULT)
                self.graphEditor.addCrossEdge(scene, id, activeNode.id)
                self.graphEditorActions.addCrossEdge_.disconnect()
                self.graphEditorActions.addCrossEdge_.connect(
                    lambda: self.onCrossEdgePress()
                )

        else:
            scene = data.scene
            activeNode = scene.activeNode()
            activeNode.setState(NodeState.MARKED)
            if activeNode:
                self.graphEditorActions.addCrossEdge_.disconnect()
                self.graphEditorActions.addCrossEdge_.connect(
                    lambda: self.onCrossEdgePress(scene, activeNode.id)
                )
