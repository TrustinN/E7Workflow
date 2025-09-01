from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QComboBox, QGraphicsView, QVBoxLayout, QWidget

from ..graph.editor import GraphEditor, GraphEditorActions
from ..workspace.editor import WorkspacEditorActions, WorkspaceEditor


class EditorWidget(QWidget):
    workspaceCreated_ = pyqtSignal(object)
    edgeCreated_ = pyqtSignal(object)
    crossEdgeCreated_ = pyqtSignal(object)

    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.wksEditor: WorkspaceEditor = WorkspaceEditor()
        self.wksEditorActions: WorkspacEditorActions = WorkspacEditorActions()

        self.graphEditor: GraphEditor = GraphEditor()
        self.graphEditorActions: GraphEditorActions = GraphEditorActions()

        self.graphView = QGraphicsView()
        self.graphView.setFixedSize(400, 300)
        self.graphView.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.graphView.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.actions = QComboBox()

        self.layout.addWidget(self.actions)
        self.layout.addWidget(self.wksEditorActions)
        self.layout.addWidget(self.graphEditorActions)
        self.layout.addWidget(self.graphView)

        self.wksEditorActions.add_.connect(self.addWorkspace)
        self.graphEditor.edgeCreated_.connect(self.edgeCreated_)
        self.graphEditor.crossEdgeCreated_.connect(self.crossEdgeCreated_)

    def setActions(self, actions):
        for action in actions:
            self.actions.addItem(action)

    def addWorkspace(self, id=None, name=None):
        wks = self.wksEditor.addWorkspace(id, name)
        self.workspaceCreated_.emit(wks)

    def addNode(self, scene, id, name=None):
        return self.graphEditor.addNode(scene, id, name)

    def addEdge(self, scene):
        self.graphEditor.addEdge(scene)
