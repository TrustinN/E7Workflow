from PyQt5.QtWidgets import QWidget

from src.app.frontend.models import GraphModel
from src.app.frontend.state import SelectionModel

from .node import RunnerNode
from .widget import RunnerButtons


class RunnerComponent(QWidget):
    def __init__(self, selectionModel: SelectionModel):
        super().__init__()

        self.buttons = RunnerButtons()
        self.model = GraphModel()
        self.node = RunnerNode(self.model, selectionModel, self.buttons)
