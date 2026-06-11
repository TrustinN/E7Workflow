from PyQt5.QtCore import pyqtSignal

from .models import Model


class SelectionModel(Model):
    selected_ = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.prevSelected = None
        self.selected = None

    def setSelected(self, id):
        self.prevSelected = self.selected
        self.selected = id
        self.selected_.emit(id)

    def getSelected(self):
        return self.selected

    def hasSelected(self):
        return self.setSelected is not None

    def getPrevSelected(self):
        return self.prevSelected

    def clearSelection(self):
        self.prevSelected = self.selected
        self.selected = None
        self.selected_.emit(None)

    def clear(self):
        self.selected = None
        self.prevSelected = None

        self.modelClear_.emit()

    def serialize(self):
        return {
            "prev": self.prevSelected,
            "curr": self.selected,
        }

    def deserialize(self, state):
        self.prevSelected = state["prev"]
        self.selected = state["curr"]

        self.modelLoaded_.emit()
