from PyQt5.QtWidgets import QApplication, QHBoxLayout, QMainWindow, QWidget

from .frontend.events import PubSubHandler
from .frontend.graph import GraphComponent

# from .frontend.runner import RunnerComponent
from .frontend.workspace import WorkspaceComponent


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

    def closeEvent(self, event):
        QApplication.quit()


class App(QApplication):
    def __init__(self):
        super().__init__([])

        self.window = MainWindow()
        self.widget = QWidget()
        self.layout = QHBoxLayout()
        self.widget.setLayout(self.layout)
        self.window.setCentralWidget(self.widget)
        self.window.show()

        self.wkCpt = WorkspaceComponent()
        self.graphCpt = GraphComponent()
        # self.runnerCpt = RunnerComponent(self.ctxManager)

        self.layout.addWidget(self.wkCpt.widget)
        self.layout.addWidget(self.graphCpt)
        # self.layout.addWidget(self.runnerCpt.widget)

        self.pubSubHandler = PubSubHandler()
        self.pubSubHandler.registerNode(self.wkCpt)
        self.pubSubHandler.registerNode(self.graphCpt.miniViewNode)
        self.pubSubHandler.handlePublish("/App/Loaded")
