from PyQt5.QtWidgets import QPushButton, QVBoxLayout, QWidget

from src.app.backend.action import ActionRoute, ActionType
from src.app.frontend.state import WorkspaceContext
from src.router.routing import Client, Dispatcher, Link

from .node import RunnerNode
from .widget import RunnerWidget


class RunnerComponent(QWidget):
    def __init__(self, context: WorkspaceContext, dispatcher: Dispatcher):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.setActionBtn = QPushButton("Set Action")
        self.widget = RunnerWidget()

        self.layout.addWidget(self.setActionBtn)
        self.layout.addWidget(self.widget)
        self.layout.addStretch()

        self.client = Client("Runner Component", dispatcher)
        self.addAction(ActionType.CLICK)
        self.addAction(ActionType.DRAG)

        self.context = context
        self.node = RunnerNode(self.context, dispatcher)

        self.setActionBtn.clicked.connect(self.setAction)

    def addAction(self, name):
        infoLink = Link(ActionRoute.NAME, ActionRoute.ACTION, name)
        info = self.client.get(infoLink)

        self.widget.addAction(info)

    def setAction(self):
        data = self.widget.getActionData()
        self.node.setAction(data)
