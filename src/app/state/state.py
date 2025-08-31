import json

from pydantic import BaseModel
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QTextEdit, QVBoxLayout, QWidget


class StateData(BaseModel):
    entrypoint: str = ""
    userstate: dict = {}


class StateWidget(QWidget):
    stateModified_ = pyqtSignal(object)

    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.display = QTextEdit()

        self.layout.addWidget(self.display)

    def renderState(self, state: StateData):
        self.display.setText(state.model_dump_json(indent=2))

    def recompileState(self):
        state = StateData(**json.loads(self.display.toPlainText()))
        self.renderState(state)
        self.stateModified_.emit(state)
