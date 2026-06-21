from PyQt5.QtCore import QObject, pyqtSignal


class GraphicsEmitter(QObject):
    onMove = pyqtSignal()
    onMousePress = pyqtSignal()
