from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from .components.data import DataWidget
from .components.editor import EditorWidget
from .components.manager import WorkspaceManager
from .components.runner import RunnerWidget
from .components.serializer import AppSerializer, AppState
from .constants import ROOT_ID
from .graph.graph import NODE_HIGHLIGHT_COLOR
from .workspace.helpers import actions


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

        self.editor = EditorWidget()
        self.manager = WorkspaceManager()
        self.runner = RunnerWidget(self.manager.sendData_)
        self.dataDisplay = DataWidget()
        self.serializer = AppSerializer(self)

        self.importBtn = QPushButton("Import")
        self.exportBtn = QPushButton("Export")

        self.layout.addWidget(self.editor)
        self.col2Layout.addWidget(self.dataDisplay)
        self.col2Layout.addWidget(self.runner)
        self.layout.addLayout(self.col2Layout)
        self.col3Layout.addWidget(self.importBtn)
        self.col3Layout.addWidget(self.exportBtn)
        self.layout.addLayout(self.col3Layout)

        self.initSignals()
        self.initState()

    def initSignals(self):
        self.editor.workspaceCreated_.connect(self.manager.registerWorkspace)
        self.manager.workspaceRegistered.connect(self.onWorkspaceRegistered)
        self.manager.dataUpdate.connect(self.dataDisplay.renderData)

        # Change InteractiveGraphicsScene on active workspace change
        self.manager.activeChanged.connect(
            lambda id: self.editor.graphView.setScene(self.manager.scene(id))
        )

        # Add edge to scene on button press
        self.editor.graphEditorActions.addEdge_.connect(
            lambda: self.editor.addEdge(self.manager.scene())
        )

        # Update action of focused workspace
        self.editor.actions.currentTextChanged.connect(self.onActionChanged)

        # Poll data from manager
        self.runner.resolver.getData_.connect(self.manager.sendData)

        self.runner.requestData_.connect(self.manager.sendData)
        self.manager.sendData_.connect(self.runner.setData)

        self.importBtn.clicked.connect(self.importConfig)
        self.exportBtn.clicked.connect(self.exportConfig)

    def initState(self):
        self.editor.setActions(actions)
        self.manager.initState()

    def reset(self):
        self.manager.reset()
        self.runner.reset()
        self.dataDisplay.reset()

    def onWorkspaceRegistered(self, id):
        parentID = self.manager.parentID(id)
        wks = self.manager.workspace(id)
        data = self.manager.data(id)
        node = self.editor.addNode(self.manager.scene(parentID), id, wks.name)

        wks.mousePress.connect(lambda: self.dataDisplay.setData(data))
        node.emitter.onMousePress_.connect(lambda: self.onNodeMousePress(id))

    def onNodeMousePress(self, id):
        wks = self.manager.workspace(id)
        data = self.manager.data(id)

        self.dataDisplay.setData(data)
        highlightColor = QColor(NODE_HIGHLIGHT_COLOR)
        highlightColor.setAlpha(NODE_HIGHLIGHT_COLOR.alpha() // 4)
        wks.setColor(highlightColor, NODE_HIGHLIGHT_COLOR)
        wks.raise_()
        self.editor.actions.setCurrentText(data.action.__name__)

    def onActionChanged(self, action: str):
        activeScene = self.manager.scene()
        if activeScene:
            activeNode = activeScene.activeNode()
            if activeNode:
                self.manager.setAction(activeNode.id, action)

    def importConfig(self):
        self.reset()
        self.applySnapshot()

    def exportConfig(self):
        state = AppState(self.manager.data(ROOT_ID), self.runner.state)

        self.serializer.reset()
        self.serializer.snapshot(state)
        self.serializer.writeData("snapshot")

    def applySnapshot(self):
        self.serializer.reset()
        self.serializer.readData("snapshot")
        self.serializer.playLogs()
