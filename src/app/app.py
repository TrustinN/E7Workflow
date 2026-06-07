from PyQt5.QtWidgets import QApplication, QHBoxLayout, QMainWindow, QWidget

from .frontend.events import PubSubHandler
from .frontend.graph import GraphComponent

# from .frontend.runner import RunnerComponent
from .frontend.state import SelectionModel, SelectionModelNode
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

        self.selectionModel = SelectionModel()
        self.selectionNode = SelectionModelNode(self.selectionModel)

        self.wkCpt = WorkspaceComponent(self.selectionModel)
        self.graphCpt = GraphComponent(self.selectionModel)
        # self.runnerCpt = RunnerComponent(self.ctxManager)

        self.layout.addWidget(self.wkCpt)
        self.layout.addWidget(self.graphCpt)
        # self.layout.addWidget(self.runnerCpt.widget)

        self.pubSubHandler = PubSubHandler()
        self.pubSubHandler.registerNode(self.wkCpt.node)
        self.pubSubHandler.registerNode(self.graphCpt.graphNode)
        self.pubSubHandler.registerNode(self.selectionNode)
        self.pubSubHandler.handlePublish("/App/Loaded")
