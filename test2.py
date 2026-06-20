from typing import Optional

from PyQt5.QtCore import QRectF, Qt
from PyQt5.QtGui import QBrush, QColor, QPainter, QPen
from PyQt5.QtWidgets import (
    QApplication,
    QGraphicsItem,
    QGraphicsObject,
    QGraphicsScene,
    QGraphicsView,
    QMainWindow,
    QStyleOptionGraphicsItem,
    QVBoxLayout,
    QWidget,
)


class Window(QGraphicsObject):
    def __init__(self, parent: Optional[QGraphicsItem] = None):
        super().__init__(parent)

        self.color = QColor(255, 255, 255, 20)
        self.borderColor = QColor(255, 255, 255, 40)
        self.padding = 0
        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsMovable
            | QGraphicsItem.GraphicsItemFlag.ItemIsFocusable
            | QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
            | QGraphicsItem.GraphicsItemFlag.ItemClipsChildrenToShape
        )

    def boundingRect(self) -> QRectF:
        penWidth = 1
        return QRectF(
            -10 - penWidth / 2,
            -10 - penWidth / 2,
            20 + penWidth,
            20 + penWidth,
        )

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionGraphicsItem,
        widget: Optional[QWidget] = None,
    ):
        painter.drawRoundedRect(-10, -10, 20, 20, 5, 5)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

    def closeEvent(self, event):
        QApplication.quit()


class App(QApplication):
    def __init__(self):
        super().__init__([])
        self.window = MainWindow()
        self.window.setWindowTitle("Transparent Background")
        self.window.setWindowFlags(Qt.FramelessWindowHint)
        self.window.setAttribute(Qt.WA_TranslucentBackground)
        self.widget = QWidget()
        self.widget.setWindowTitle("Transparent Background")
        self.widget.setWindowFlags(Qt.FramelessWindowHint)
        self.widget.setAttribute(Qt.WA_TranslucentBackground)
        self.layout = QVBoxLayout(self.widget)

        self.widget.setLayout(self.layout)
        self.window.setCentralWidget(self.widget)
        self.window.show()

        self.scene = QGraphicsScene()
        self.scene.setSceneRect(-100000, -100000, 200000, 200000)
        self.view = QGraphicsView(self.scene)
        self.view.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)

        self.view.setAttribute(Qt.WA_TranslucentBackground)
        self.view.viewport().setWindowOpacity(0.2)
        self.view.setAutoFillBackground(False)
        self.scene.setBackgroundBrush(QBrush(Qt.NoBrush))
        self.view.setBackgroundBrush(QBrush(Qt.NoBrush))

        self.view.setBackgroundBrush(QBrush(QColor(0, 0, 0, 30)))  # 30/255 alpha

        self.scene.setBackgroundBrush(QBrush(QColor(0, 0, 0, 30)))

        self.scene.addItem(Window())
        self.layout.addWidget(self.view)


app = App()
app.exec()
