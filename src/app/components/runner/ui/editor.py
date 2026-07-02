from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QHBoxLayout, QPushButton, QSlider, QVBoxLayout, QWidget

from src.app.actions import ActionRegistry
from src.app.components.runner.model import RunnerModel
from src.app.state import Context

from .edge import EdgeEditor
from .node import ActionEditor


class FloatSlider(QSlider):
    valueChangedFloat = pyqtSignal(float)

    def __init__(self, orientation: Qt.Orientation, parent=None):
        super().__init__(orientation, parent)

        self._min = 0.0
        self._max = 1.0
        self._decimals = 2

        self.setRange(0, 1000)
        self.valueChanged.connect(self._emitFloat)

    def setFloatRange(self, minimum: float, maximum: float):
        self._min = minimum
        self._max = maximum
        self.update()

    def setDecimals(self, decimals: int):
        self._decimals = decimals
        self.update()

    def floatValue(self) -> float:
        return self._min + (self.value() / self.maximum()) * (self._max - self._min)

    def setFloatValue(self, value: float):
        self.setValue(
            int((value - self._min) / (self._max - self._min) * self.maximum())
        )

    def _emitFloat(self, _):
        self.valueChangedFloat.emit(self.floatValue())
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)

        painter = QPainter(self)
        text = f"{self.floatValue():.{self._decimals}f}"

        painter.drawText(
            self.rect(),
            Qt.AlignCenter,
            text,
        )


class RunnerEditor(QWidget):

    def __init__(self, context: Context, model: RunnerModel, actions: ActionRegistry):
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

        speed = FloatSlider(Qt.Orientation.Horizontal)
        speed.setFloatRange(0.5, 2.0)
        speed.valueChanged.connect(lambda: model.setSpeed(speed.floatValue()))
        model.modelLoaded.connect(lambda: speed.setFloatValue(model.getSpeed()))
        model.modelCleared.connect(lambda: speed.setFloatValue(model.getSpeed()))

        action = actions.get("Set Entry")
        self.entryBtn = QPushButton(actions.displayText("Set Entry"))
        self.entryBtn.clicked.connect(action.trigger)

        action = actions.get("Execute")
        self.executeBtn = QPushButton(actions.displayText("Execute"))
        self.executeBtn.clicked.connect(action.trigger)

        actionRow = QHBoxLayout()
        actionRow.addWidget(self.setActionBtn)
        actionRow.addWidget(self.unsetActionBtn)

        scriptRow = QHBoxLayout()
        scriptRow.addWidget(self.setScriptBtn)
        scriptRow.addWidget(self.unsetScriptBtn)

        actionEditor = ActionEditor(context, model)
        edgeEditor = EdgeEditor(context, model)

        self.layout.addLayout(actionRow)
        self.layout.addLayout(scriptRow)
        self.layout.addWidget(speed)
        self.layout.addWidget(self.entryBtn)
        self.layout.addWidget(self.executeBtn)
        self.layout.addWidget(actionEditor)
        self.layout.addWidget(edgeEditor)
