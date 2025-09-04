from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtWidgets import QPushButton, QVBoxLayout, QWidget

from ..components.manager import WORKSPACE_MANAGER
from ..graph.graph import NodeType
from ..routing import Dispatcher, Endpoint, Packet
from .data import WorkspaceData
from .state import RunnerState, StateWidget

RUN_RESOLVER = "Run Resolver"
RUNNER = "Runner"


class RunResolver(QObject):
    def __init__(self, dispatcher: Dispatcher):
        super().__init__()
        self.name = RUN_RESOLVER
        self.endpoint = Endpoint(self.name, dispatcher)
        self.endpoint.addHandler(self.name, self.receiveData)

    def receiveData(self, packet: Packet):
        self.data = packet.data["data"]

    def getData(self, id=None):
        self.endpoint.send({"type": "GET", "id": id}, receiver=WORKSPACE_MANAGER)

    def getRunnableData(self, id=None):
        self.getData(id)
        if len(self.data.childData) != 0:
            entry = self.data.defaultChildEntryNodeID
            if entry:
                self.getRunnableData(entry)

    def next(self):
        if len(self.data.edges) > 0:
            self.getRunnableData(self.data.edges[0])
            return True

        return False

    def runnable(self):
        if self.data.action is None or self.data.workspace is None:
            return None

        def exec():
            self.data.action(self.data.workspace)

        return exec


class RunnerWidget(QWidget):
    stateUpdate_ = pyqtSignal(object)

    def __init__(self, dispatcher: Dispatcher):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.data: WorkspaceData = None

        self.state = RunnerState()
        self.stateView = StateWidget()
        self.stateView.renderState(self.state)

        self.resolver = RunResolver(dispatcher)

        self.runBtn = QPushButton("Run")
        self.updateStateBtn = QPushButton("Update State")
        self.setEntrypointBtn = QPushButton("Set Entrypoint")
        self.setLocalEntrypointBtn = QPushButton("Set Local Entrypoint")

        self.stateUpdate_.connect(self.stateView.renderState)
        self.runBtn.clicked.connect(lambda: self.run())
        self.updateStateBtn.clicked.connect(self.stateView.recompileState)
        self.stateView.stateModified_.connect(self.setState)
        self.setEntrypointBtn.clicked.connect(self.setEntrypoint)
        self.setLocalEntrypointBtn.clicked.connect(self.setLocalEntrypoint)

        self.layout.addWidget(self.stateView)
        self.layout.addWidget(self.updateStateBtn)
        self.layout.addWidget(self.setEntrypointBtn)
        self.layout.addWidget(self.setLocalEntrypointBtn)
        self.layout.addWidget(self.runBtn)

    def receiveData(self, packet: Packet):
        self.data = packet.data["data"]

    def getData(self, id=None):
        self.endpoint.send({"type": "GET", "id": id}, receiver=WORKSPACE_MANAGER)

    def setEntrypoint(self):
        self.getData()

        data = self.data
        activeNode = data.scene.activeNode()
        id = None
        if activeNode:
            id = activeNode.id
        else:
            return

        if id == self.state.entrypoint:
            return

        if self.state.entrypoint:
            self.getData(self.state.entrypoint)
            prevData = self.data
            prevData.node.setType(NodeType.DEFAULT)

        self.state.entrypoint = id
        self.stateUpdate_.emit(self.state)
        activeNode.setType(NodeType.GLOBAL_ENTRYPOINT)

    def setEntrypointByID(self, id):
        self.getData(id)

        data = self.data
        node = data.node

        if id == self.state.entrypoint:
            return

        if self.state.entrypoint:
            self.getData(self.state.entrypoint)
            prevData = self.data
            prevData.node.setType(NodeType.DEFAULT)

        self.state.entrypoint = id
        self.stateUpdate_.emit(self.state)
        node.setType(NodeType.GLOBAL_ENTRYPOINT)

    def setLocalEntrypoint(self):
        self.getData()

        data = self.data
        parentData = data.parentData
        activeNode = data.scene.activeNode()
        id = None
        if activeNode:
            id = activeNode.id

        if parentData is None:
            return

        if id == parentData.defaultChildEntryNodeID:
            return

        prevID = data.defaultChildEntryNodeID
        if prevID:
            self.getData(prevID)
            prevData = self.data
            prevData.node.setType(NodeType.DEFAULT)

        data.defaultChildEntryNodeID = id
        activeNode.setType(NodeType.LOCAL_ENTRYPOINT)

    def setLocalEntrypointByID(self, id):
        self.getData(id)

        data = self.data
        parentData = data.parentData
        node = data.node

        if parentData is None:
            return

        if id == parentData.defaultChildEntryNodeID:
            return

        prevID = parentData.defaultChildEntryNodeID
        if prevID:
            self.getData(prevID)
            prevData = self.data
            prevData.node.setType(NodeType.DEFAULT)

        parentData.defaultChildEntryNodeID = id
        node.setType(NodeType.LOCAL_ENTRYPOINT)

    def setState(self, state: RunnerState):
        self.setEntrypointByID(state.entrypoint)
        self.state.userstate = state.userstate
        self.stateUpdate_.emit(self.state)

    def reset(self):
        self.state = RunnerState()
        self.data = None

    def run(self, maxIter=10):
        # Define entry workspace
        self.resolver.getRunnableData(self.state.entrypoint)

        for i in range(maxIter):
            advance = self.resolver.runnable()
            if advance is None:
                break

            advance()

            if not self.resolver.next():
                break


RUNNER_SERVICE = "RUNNER SERVICE"


class RunnerService:
    def __init__(self, dispatcher: Dispatcher):
        self.endpoint = Endpoint(RUNNER_SERVICE, dispatcher)
        self.endpoint.addHandler(RUNNER_SERVICE, self.receiveData)

    def receiveData(self, packet: Packet):
        data = packet.data

        type_ = data["type"]
        match type_:
            case "GET":
                self.handleGetRequest(packet)
            case "POST":
                self.handlePostRequest(packet)

    def handleGetRequest(self, packet: Packet):
        data = packet.data
        sender = packet.sender

        id = data["id"]
        self.sendData(self.editor.workspace(id), receiver=sender)
