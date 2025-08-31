from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtWidgets import QPushButton, QVBoxLayout, QWidget

from ..state.state import StateData, StateWidget
from .data import WorkspaceData


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

    def next(self):
        if len(self.data.edges) > 0:
            self.getData(self.data.edges[0])
            return True

        return False

    def runnable(self):
        if self.data.action is None or self.data.workspace is None:
            return None

        def exec():
            self.data.action(self.data.workspace)

        return exec


class RunnerWidget(QWidget):
    requestEntrypoint = pyqtSignal()
    stateUpdate_ = pyqtSignal(object)

    def __init__(self, dataReceiver):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.state = StateData()
        self.stateView = StateWidget()
        self.stateView.renderState(self.state)

        self.resolver = RunResolver(dataReceiver)

        self.runBtn = QPushButton("Run")
        self.updateStateBtn = QPushButton("Update State")
        self.setEntrypointBtn = QPushButton("Set Entrypoint")

        self.stateUpdate_.connect(self.stateView.renderState)
        self.runBtn.clicked.connect(self.run)
        self.updateStateBtn.clicked.connect(self.stateView.recompileState)
        self.stateView.stateModified_.connect(self.setState)
        self.setEntrypointBtn.clicked.connect(self.getEntrypoint)

        self.layout.addWidget(self.stateView)
        self.layout.addWidget(self.updateStateBtn)
        self.layout.addWidget(self.setEntrypointBtn)
        self.layout.addWidget(self.runBtn)

    def getEntrypoint(self):
        self.requestEntrypoint.emit()

    def setEntrypoint(self, id):
        self.state.entrypoint = id
        self.stateUpdate_.emit(self.state)

    def setState(self, state: StateData):
        self.state = state
        self.stateUpdate_.emit(self.state)

    def run(self, maxIter=10):
        # Define entry workspace
        self.resolver.getData(self.state.entrypoint)

        for i in range(maxIter):
            advance = self.resolver.runnable()
            if advance is None:
                break

            advance()

            if not self.resolver.next():
                break
