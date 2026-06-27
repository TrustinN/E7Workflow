from PyQt5.QtWidgets import QPushButton, QVBoxLayout, QWidget

from src.app.actions import ActionRegistry


class RunnerEditor(QWidget):

    def __init__(self, actions: ActionRegistry):
        super().__init__()

        self.layout = QVBoxLayout(self)

        action = actions.get("Set Action")
        self.setActionBtn = QPushButton(actions.displayText("Set Action"))
        self.setActionBtn.clicked.connect(action.trigger)

        action = actions.get("Unset Action")
        self.unsetActionBtn = QPushButton(actions.displayText("Unset Action"))
        self.unsetActionBtn.clicked.connect(action.trigger)

        action = actions.get("Set Script")
        self.setScriptBtn = QPushButton(actions.displayText("Set Script"))
        self.setScriptBtn.clicked.connect(action.trigger)

        action = actions.get("Unset Script")
        self.unsetScriptBtn = QPushButton(actions.displayText("Unset Script"))
        self.unsetScriptBtn.clicked.connect(action.trigger)

        action = actions.get("Set Entry")
        self.entryBtn = QPushButton(actions.displayText("Set Entry"))
        self.entryBtn.clicked.connect(action.trigger)

        action = actions.get("Execute")
        self.executeBtn = QPushButton(actions.displayText("Execute"))
        self.executeBtn.clicked.connect(action.trigger)

        self.layout.addWidget(self.setActionBtn)
        self.layout.addWidget(self.unsetActionBtn)
        self.layout.addWidget(self.setScriptBtn)
        self.layout.addWidget(self.unsetScriptBtn)
        self.layout.addWidget(self.entryBtn)
        self.layout.addWidget(self.executeBtn)
