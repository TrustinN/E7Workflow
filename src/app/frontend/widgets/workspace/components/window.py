import numpy as np
from PyQt5.QtCore import QPoint, QRect, Qt, pyqtSignal
from PyQt5.QtGui import QBrush, QColor, QPainter, QPen, QRegion
from PyQt5.QtWidgets import QWidget

from .utils.colors import Colors


class SelectionWindow(QWidget):
    resizeSignal = pyqtSignal()
    moveSignal = pyqtSignal()

    def __init__(self, name=None):
        super().__init__()
        self.name = name

        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.color = Colors.DEFAULT_COLOR
        self.borderColor = Colors.DEFAULT_BORDER

        super().setGeometry(500, 500, 500, 300)
        self.dragPosition = QPoint()
        self.resizeMode = False
        self.resizeIndices = None
        self.resizeError = (np.array([0.0, 0.0]), np.array([0.0, 0.0]))
        self.fixed = False

    def grabMouse(self) -> bool:
        if not self.canMove():
            return False
        self.setFocus()
        self.raise_()
        self.activateWindow()
        super().grabMouse()
        return True

    def mouseMoveEvent(self, event):
        if not self.canMove():
            return

        if not self.resizeMode:
            self.move(event.globalPos() - self.dragPosition)
            self.moveSignal.emit()
            return

        corners = self.getBBox()
        for i in self.resizeIndices:
            if i % 2 == 0:
                corners[i // 2].setX(event.globalPos().x())
            else:
                corners[i // 2].setY(event.globalPos().y())

        self.setGeometry(QRect(corners[0], corners[1]))
        self.resizeSignal.emit()

    def mousePressUpdate(self, event):
        self.dragPosition = event.globalPos() - self.frameGeometry().topLeft()

        threshold = 10
        dragx = self.dragPosition.x()
        dragy = self.dragPosition.y()
        sideActive = [
            0 <= dragx and dragx <= threshold,
            0 <= dragy and dragy <= threshold,
            self.width() - threshold <= dragx and dragx <= self.width(),
            self.height() - threshold <= dragy and dragy <= self.height(),
        ]
        activeCnt = [1 if v else 0 for v in sideActive]

        inX = 0 <= dragx and dragx <= self.width()
        inY = 0 <= dragy and dragy <= self.height()
        inside = inX and inY

        if not sum(activeCnt) or not inside or not self.canMove():
            if not inside:
                self.mouseReleaseEvent(event)
            self.resizeMode = False
        else:
            self.resizeMode = True
            self.resizeIndices = [i for i, x in enumerate(activeCnt) if x == 1]

    def mousePressEvent(self, event):
        self.mousePressUpdate(event)

        if self.canMove():
            self.grabMouse()

    def mouseReleaseEvent(self, event):
        self.releaseMouse()

    def resizeEvent(self, event):
        maskedRegion = QRegion(
            self.rect(),
            QRegion.RegionType.Rectangle,
        )
        self.setMask(maskedRegion)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        brush = QBrush(self.color)
        painter.setBrush(brush)

        pen = QPen(self.borderColor)
        painter.setPen(pen)

        rect = self.rect()
        painter.drawRect(rect.adjusted(1, 1, -1, -1))

        if self.name is not None:
            painter.setPen(QPen(QColor(255, 255, 255), 1))
            font = painter.font()
            font.setPointSize(12)
            font.setBold(False)
            painter.setFont(font)

            paddingTop = 10
            textRect = rect.adjusted(0, paddingTop, 0, 0)
            painter.drawText(textRect, Qt.AlignTop | Qt.AlignHCenter, self.name)

    def getBBox(self):
        return [
            self.frameGeometry().topLeft(),
            self.frameGeometry().bottomRight(),
        ]

    def setName(self, name):
        self.name = name
        self.repaint()

    def setColor(self, color, borderColor):
        self.color = color
        self.borderColor = borderColor
        self.repaint()

    def getColor(self):
        return self.color

    def lock(self):
        self.fixed = True

    def unlock(self):
        self.fixed = False

    def canMove(self):
        return not self.fixed
