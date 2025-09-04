from PyQt5.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from .graph.controller import GraphController
from .graph.graph import InteractiveGraphScene
from .graph.model import GraphModel
from .graph.view import GraphView
from .graph.widget import GraphWidget
from .routing import Dispatcher

DATA_DISPLAY = "Data Display"


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
        self.col2Layout = QVBoxLayout()
        self.col3Layout = QVBoxLayout()
        self.widget.setLayout(self.layout)
        self.window.setCentralWidget(self.widget)
        self.window.show()

        self.dispatcher = Dispatcher()
        scene = InteractiveGraphScene()
        self.graphView = GraphView(scene)
        self.graphModel = GraphModel()
        self.graphController = GraphController(self.graphModel, self.graphView)
        self.graphWidget = GraphWidget(self.graphController)
        self.graphWidget.setScene(scene)
        # self.editor = EditorWidget(self.dispatcher)
        # self.manager = WorkspaceManager(self.dispatcher)
        # self.runner = RunnerWidget(self.dispatcher)
        # self.dataDisplay = DataWidget()

        self.importBtn = QPushButton("Import")
        self.exportBtn = QPushButton("Export")

        self.layout.addWidget(self.graphWidget)
        # self.col2Layout.addWidget(self.dataDisplay)
        # self.col2Layout.addWidget(self.runner)
        # self.layout.addLayout(self.col2Layout)
        # self.col3Layout.addWidget(self.importBtn)
        # self.col3Layout.addWidget(self.exportBtn)
        # self.layout.addLayout(self.col3Layout)

        # self.initSignals()
        # self.initState()

    # def initSignals(self):
    #     self.editor.workspaceCreated_.connect(self.manager.registerWorkspace)
    #
    #     self.manager.workspaceRegistered.connect(self.onWorkspaceRegistered)
    #     self.manager.dataUpdate.connect(self.dataDisplay.renderData)
    #
    #     # Change InteractiveGraphicsScene on active workspace change
    #     self.manager.activeChanged.connect(
    #         lambda id: self.editor.graphView.setScene(self.manager.scene(id))
    #     )
    #
    #     # Update action of focused workspace
    #     self.editor.actions.currentTextChanged.connect(self.onActionChanged)
    #
    #     # Poll data from manager
    #     # TODO: Send and receive data too complicated remove the signal from manager
    #     # and just have a function to receive the data from the widget receiving
    #     # then in that receive function, we can just emit a received data signal
    #
    #     self.importBtn.clicked.connect(self.importConfig)
    #     self.exportBtn.clicked.connect(self.exportConfig)

    # def initState(self):
    #     self.editor.setActions(actions)
    #     self.manager.initState()

    def reset(self):
        self.manager.reset()
        self.runner.reset()
        self.dataDisplay.reset()

    # def onActionChanged(self, action: str):
    #     activeScene = self.manager.scene()
    #     if activeScene:
    #         activeNode = activeScene.activeNode()
    #         if activeNode:
    #             self.manager.setAction(activeNode.id, action)

    def importConfig(self):
        self.reset()
        self.applySnapshot()

    def exportConfig(self):

        self.serializer.reset()
        # self.serializer.snapshot(state)
        self.serializer.writeData("snapshot")

    def applySnapshot(self):
        self.serializer.reset()
        self.serializer.readData("snapshot")
        self.serializer.playLogs()
