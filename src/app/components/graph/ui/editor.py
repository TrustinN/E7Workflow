from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QGraphicsView, QPushButton, QShortcut, QVBoxLayout, QWidget

from src.app.components.graph.model import GraphDocument, GraphModel, GraphViewState
from src.app.state import Context, SelectionType

from .controllers import FullViewController, MiniViewController
from .scene import GraphScene
from .viewmodel import GraphViewModel


class GraphEditor(QWidget):
    requestEdge = pyqtSignal(str, str)

    def __init__(self, context: Context, model: GraphModel):
        super().__init__()

        self.context = context
        self.layout = QVBoxLayout(self)
        self.document = GraphDocument(model)

        self.miniViewState = GraphViewState()
        self.fullViewState = GraphViewState()

        self.document.addViewState("miniView", self.miniViewState)
        self.document.addViewState("fullView", self.fullViewState)

        self.miniScene = GraphScene()
        self.miniController = MiniViewController(context, self.miniScene, model)
        self.miniViewModel = GraphViewModel(self.miniScene, model, self.miniViewState)
        self.miniView = QGraphicsView(self.miniScene)

        self.fullScene = GraphScene()
        self.fullController = FullViewController(context, self.fullScene, model)
        self.fullViewModel = GraphViewModel(self.fullScene, model, self.fullViewState)
        self.fullView = QGraphicsView(self.fullScene)

        self.e1Shortcut = QShortcut("1", self)
        key = self.e1Shortcut.key().toString(QKeySequence.NativeText)
        self.e1Btn = QPushButton(f"Set Edge Start ({key})")
        self.e1Shortcut.activated.connect(self.setE1)
        self.e1Btn.clicked.connect(self.setE1)

        self.e2Shortcut = QShortcut("2", self)
        key = self.e2Shortcut.key().toString(QKeySequence.NativeText)
        self.e2Btn = QPushButton(f"Set Edge End ({key})")
        self.e2Shortcut.activated.connect(self.setE2)
        self.e2Btn.clicked.connect(self.setE2)

        self.edgeShortcut = QShortcut("E", self)
        key = self.edgeShortcut.key().toString(QKeySequence.NativeText)
        self.edgeBtn = QPushButton(f"Create Edge ({key})")
        self.edgeShortcut.activated.connect(self.setEdge)
        self.edgeBtn.clicked.connect(self.setEdge)

        self.e1 = None
        self.e2 = None

        self.layout.addWidget(self.miniView)
        self.layout.addWidget(self.fullView)
        self.layout.addWidget(self.e1Btn)
        self.layout.addWidget(self.e2Btn)
        self.layout.addWidget(self.edgeBtn)

    def setE1(self):
        selection = self.context.selectionModel.getSelected()
        if selection.id and selection.type == SelectionType.WORKSPACE:
            self.e1 = selection.id

    def setE2(self):
        selection = self.context.selectionModel.getSelected()
        if selection.id and selection.type == SelectionType.WORKSPACE:
            self.e2 = selection.id

    def setEdge(self):
        if not (self.e1 and self.e2):
            return

        self.requestEdge.emit(self.e1, self.e2)
        self.e1 = None
        self.e2 = None
