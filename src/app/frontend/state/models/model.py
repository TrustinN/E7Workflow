from PyQt5.QtCore import QObject, pyqtSignal


class Model(QObject):
    modelClear_ = pyqtSignal()
    modelReset_ = pyqtSignal()

    def __init__(self):
        super().__init__()

    def clear(self):
        pass

    def serialize(self):
        pass

    def deserialize(self, state):
        pass
