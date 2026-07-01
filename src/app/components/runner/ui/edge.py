from PyQt5.QtWidgets import QHBoxLayout, QLabel, QSpinBox, QWidget

from src.app.components.runner.model import RunnerModel
from src.app.state import Context, Selection, SelectionType


class EdgeEditor(QWidget):
    def __init__(self, context: Context, model: RunnerModel):
        super().__init__()

        self.context = context
        self.model = model

        self.layout = QHBoxLayout(self)

        self.spin = QSpinBox()
        self.spin.valueChanged.connect(self.updateModelValue)
        self.spin.setDisabled(True)

        self.layout.addWidget(QLabel("Priority"))
        self.layout.addWidget(self.spin)

        self.context.selectionModel.selected_.connect(self.onSelectionChanged)

    def onSelectionChanged(self, selection: Selection):
        if not (selection.id and selection.type == SelectionType.EDGE):
            self.spin.setDisabled(True)
            return

        edge = self.model.getEdge(selection.id)
        self.spin.setDisabled(False)
        self.spin.setValue(edge.priority)

    def updateModelValue(self):
        selection = self.context.selectionModel.getSelected()
        self.model.updateEdge(selection.id, {"priority": self.spin.value()})
