from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget

from ..widget import RunnerWidget


class RunnerUI(QWidget):
    setLocalEntry_ = pyqtSignal()
    setGlobalEntry_ = pyqtSignal()
    restore_ = pyqtSignal()

    def __init__(self, widget: RunnerWidget):
        super().__init__()
        self.widget = widget
        self.widget.setLocalEntryBtn.clicked.connect(self.setLocalEntry_.emit)
        self.widget.setGlobalEntryBtn.clicked.connect(self.setGlobalEntry_.emit)
        self.widget.restoreRunnerBtn.clicked.connect(self.restore_.emit)
