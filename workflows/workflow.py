from PyQt5.QtCore import QObject, pyqtSignal

from workflows.state import GlobalState


class TaskData:
    RESULT = "Result"


class Task:
    def __init__(self, stateHandler):
        self.exec = stateHandler
        self.callback = []

    def chain(self, task):
        newTask = Task(self.exec)
        newTask.callback = self.callback[:]
        newTask.callback.append(task)
        return newTask

    def addTask(self, task):
        self.callback.append(task)
        return self

    def __call__(self, state: GlobalState):
        self.exec(state)
        for task in self.callback:
            task(state)


class Worker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.iterations = 1
        self.state = GlobalState()

    def setIterations(self, iterations):
        self.iterations = iterations

    def setTask(self, wkflow):
        self.wkflow = wkflow

    def setState(self, state):
        self.state = state

    def run(self):
        for i in range(self.iterations):
            self.wkflow(self.state)
            self.progress.emit(i)

        self.finished.emit()
