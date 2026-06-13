import numpy as np
from PyQt5.QtCore import QPoint, QRect, Qt, pyqtSignal
from PyQt5.QtGui import QBrush, QColor, QPainter, QPen, QRegion
from PyQt5.QtWidgets import QWidget

from src.app.frontend.widgets.utils.colors import Colors

from .utils import bboxToLayout


class Window(QWidget):
    mousePress = pyqtSignal()
    resizeSignal = pyqtSignal()
    moveSignal = pyqtSignal()

    resizeBegin = pyqtSignal()
    moveBegin = pyqtSignal()

    resizeDone = pyqtSignal()
    moveDone = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.color = Colors.DEFAULT_COLOR
        self.borderColor = Colors.DEFAULT_BORDER
        self.padding = 0

        super().setGeometry(500, 500, 500, 300)
        self.dragPosition = QPoint()
        self.resizing = False
        self.moving = False
        self.resizeIndices = []
        self.resizeError = (np.array([0.0, 0.0]), np.array([0.0, 0.0]))
        self.fixed = False

    def grabMouse(self) -> bool:
        if not self.canMove():
            return

        self.setFocus()
        self.raise_()
        self.activateWindow()
        super().grabMouse()
        self.mousePress.emit()

    def getResizeCorners(self, event):
        corners = self.getBBox()
        for i in self.resizeIndices:
            if i % 2 == 0:
                corners[i // 2].setX(event.globalPos().x())
            else:
                corners[i // 2].setY(event.globalPos().y())
        return corners

    def mouseMoveEvent(self, event):
        if not self.canMove():
            return

        if not self.resizeIndices:
            if not self.moving:
                self.moveBegin.emit()

            self.move(event.globalPos() - self.dragPosition)
            self.moving = True

            self.moveSignal.emit()
            return

        if not self.resizing:
            self.resizeBegin.emit()

        self.resizing = True
        corners = self.getResizeCorners(event)
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

        if sum(activeCnt) and inside and self.canMove():
            self.resizeIndices = [i for i, x in enumerate(activeCnt) if x == 1]

        else:
            self.resizeIndices = []

    def mousePressEvent(self, event):
        self.mousePressUpdate(event)

        if self.canMove():
            self.grabMouse()

    def mouseReleaseEvent(self, event):
        self.releaseMouse()
        self.onMovementFinish()

    def onMovementFinish(self):
        if self.resizing:
            self.resizing = False
            self.resizeDone.emit()

        elif self.moving:
            self.moving = False
            self.moveDone.emit()

    def getBBox(self):
        return [
            self.frameGeometry().topLeft(),
            self.frameGeometry().bottomRight(),
        ]

    def getGeometry(self):
        return bboxToLayout(self.getBBox())

    def setColor(self, color, borderColor):
        self.color = color
        self.borderColor = borderColor
        self.repaint()

    def setPadding(self, padding):
        prevPadding = self.padding
        self.padding = padding

        paddingChange = self.padding - prevPadding
        newRect = self.geometry().adjusted(
            -paddingChange, -paddingChange, paddingChange, paddingChange
        )
        super().setGeometry(newRect)
        self.resizeSignal.emit()

    def getColor(self):
        return self.color

    def lock(self):
        self.fixed = True

    def unlock(self):
        self.fixed = False

    def canMove(self):
        return not self.fixed

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
