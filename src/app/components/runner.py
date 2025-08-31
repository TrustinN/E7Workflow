from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtWidgets import QPushButton, QVBoxLayout, QWidget

from ..state.state import StateWidget
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
        def exec():
            self.data.action(self.data.workspace)

        return exec


class RunnerWidget(QWidget):
    def __init__(self, dataReceiver):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.state = {}
        self.stateView = StateWidget()
        self.stateView.renderState(self.state)

        self.resolver = RunResolver(dataReceiver)

        self.runBtn = QPushButton("Run")
        self.runBtn.clicked.connect(self.run)

        self.layout.addWidget(self.stateView)
        self.layout.addWidget(self.runBtn)

    def run(self, id, maxIter=10):
        # Define entry workspace
        self.resolver.getData(id)

        for i in range(maxIter):
            advance = self.resolver.runnable()
            advance()
            if not self.resolver.next():
                break
