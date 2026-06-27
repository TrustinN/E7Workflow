from PyQt5.QtWidgets import QPushButton, QVBoxLayout, QWidget

from src.app.actions import ActionRegistry
from src.app.state import Context, SelectionType


class GraphEditor(QWidget):
    def __init__(self, context: Context, actions: ActionRegistry):
        super().__init__()

        self.layout = QVBoxLayout(self)
        self.context = context

        action = actions.get("Set Edge Start")
        self.e1Btn = QPushButton(actions.displayText("Set Edge Start"))
        self.e1Btn.clicked.connect(action.trigger)

        action = actions.get("Set Edge End")
        self.e2Btn = QPushButton(actions.displayText("Set Edge End"))
        self.e2Btn.clicked.connect(action.trigger)

        action = actions.get("Create Edge")
        self.edgeBtn = QPushButton(actions.displayText("Create Edge"))
        self.edgeBtn.clicked.connect(action.trigger)

        self.layout.addWidget(self.e1Btn)
        self.layout.addWidget(self.e2Btn)
        self.layout.addWidget(self.edgeBtn)
        self.layout.addStretch()

        self.e1 = None
        self.e2 = None

    def setE1(self):
        selection = self.context.selectionModel.getSelected()
        if selection.id and selection.type == SelectionType.WORKSPACE:
            self.e1 = selection.id

    def setE2(self):
        selection = self.context.selectionModel.getSelected()
        if selection.id and selection.type == SelectionType.WORKSPACE:
            self.e2 = selection.id

    def draftEdge(self):
        if not (self.e1 and self.e2):
            return None, None

        e1, e2 = self.e1, self.e2
        self.e1, self.e2 = None, None
        return e1, e2
