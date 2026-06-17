from PyQt5.QtCore import QObject, QPointF, pyqtSignal


class GraphicsEmitter(QObject):
    onMove_ = pyqtSignal(QPointF)
    onMousePress_ = pyqtSignal()
