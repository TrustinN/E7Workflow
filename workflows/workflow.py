from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtWidgets import QApplication

from workflows.state import GlobalState


class TaskData:
    RESULT = "Result"


class Task:
    def __init__(self, stateHandler):
        self.exec = stateHandler
        self.callback = None

    def chain(self, task):
        self.callback = task

    def __call__(self, state: GlobalState):
        self.exec(state)
        if self.callback:
            self.callback(state)


class WorkflowRunner(QObject):
    stepFinished = pyqtSignal(GlobalState)
    executeFinish = pyqtSignal(GlobalState)

    def __init__(self):
        super().__init__()
        self.iterations = 1
        self.state = GlobalState()

    def setIterations(self, iterations):
        self.iterations = iterations

    def bindWorkflow(self, wkflow, wkspace):
        self.wkflow = wkflow
        self.wkspace = wkspace

    def setState(self, state):
        self.state = state

    def updateState(self, state):
        self.state.update(state)

    def run(self):
        self.wkspace.hide()
        QApplication.processEvents()
        for i in range(self.iterations):
            self.wkflow(self.state)
            self.stepFinished.emit(self.state)
        self.wkspace.show()

        self.executeFinish.emit(self.state)
