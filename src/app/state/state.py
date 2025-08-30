import json

from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtWidgets import QTextEdit, QVBoxLayout, QWidget


class StateWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.display = QTextEdit()
        self.display.textChanged.connect(self.onTextEdit)

        self.layout.addWidget(self.display)

    def renderState(self, state: dict[str, any]):
        self.display.setText(json.dumps(state))
