from PyQt5.QtCore import pyqtSignal

from .model import Model


class MappingModel(Model):
    dataSet_ = pyqtSignal(str)
    dataRemoved_ = pyqtSignal(str)

    def __init__(self):
        super().__init__()

        self.data = {}

    def setData(self, key, value):
        self.data[key] = value
        self.dataSet_.emit(key)

    def getData(self, key):
        return self.data[key]

    def hasKey(self, key):
        return key in self.data

    def delete(self, key):
        self.data.pop(key)
        self.dataRemoved_.emit(key)

    def clear(self):
        self.data = {}

        self.modelClear_.emit()

    def serialize(self):
        return self.data

    def deserialize(self, state):
        self.data = state

        self.modelLoaded_.emit()
