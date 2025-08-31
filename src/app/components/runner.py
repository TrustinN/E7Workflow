from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtWidgets import QPushButton, QVBoxLayout, QWidget

from .data import WorkspaceData
from .state import RunnerState, StateWidget


class RunResolver(QObject):
    getData_ = pyqtSignal(object)

    def __init__(self, dataReceiver):
        super().__init__()
        self.receiver = dataReceiver
        self.receiver.connect(self.setData)

    def getData(self, id=None):
        self.getData_.emit(id)

    def setData(self, data):
        self.data: WorkspaceData = data

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
    requestData_ = pyqtSignal()
    stateUpdate_ = pyqtSignal(object)

    def __init__(self, dataReceiver):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.data: WorkspaceData = None

        self.state = RunnerState()
        self.stateView = StateWidget()
        self.stateView.renderState(self.state)

        self.resolver = RunResolver(dataReceiver)

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

    def getData(self, id=None):
        self.requestData_.emit()

    def setData(self, data):
        self.data = data

    def setEntrypoint(self):
        self.getData()

        data = self.data
        scene = data.scene
        if scene:
            activeNode = scene.activeNode()
            if activeNode:
                id = activeNode.id
                self.state.entrypoint = id
                self.stateUpdate_.emit(self.state)

    def setLocalEntrypoint(self):
        self.getData()

        data = self.data
        scene = data.scene
        if scene:
            activeNode = scene.activeNode()
            if activeNode:
                data.defaultChildEntryNodeID = activeNode.id

    def setState(self, state: RunnerState):
        self.state = state
        self.stateUpdate_.emit(self.state)

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
