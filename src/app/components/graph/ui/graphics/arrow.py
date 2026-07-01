import math

from PyQt5.QtCore import QPointF, QRectF, Qt, pyqtSignal
from PyQt5.QtGui import (
    QBrush,
    QColor,
    QFontMetrics,
    QPainter,
    QPainterPath,
    QPainterPathStroker,
    QPen,
    QPolygonF,
)
from PyQt5.QtWidgets import QApplication, QGraphicsItem, QGraphicsObject

from .node import GraphicsNode


class GraphicsArrowItem(QGraphicsObject):
    moved = pyqtSignal()
    mousePressed = pyqtSignal()

    def __init__(self, start: GraphicsNode, end: GraphicsNode):
        super().__init__()
        self.color = QColor(255, 255, 255)
        self.highlightColor = QColor(0, 163, 255)
        self.label = ""
        self.minLabelLength = 80

        self.start = start
        self.start.moved.connect(self.onNodeMove)

        self.end = end
        self.end.moved.connect(self.onNodeMove)

        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setZValue(-1)

    def getData(self):
        return {
            "visible": self.isVisible(),
            "label": self.label,
        }

    def setData(self, data):
        visible = data.get("visible")
        label = data.get("label")

        if visible is not None:
            self.setVisible(visible)

        if label is not None:
            self.label = label

        self.update()

    def onNodeMove(self):
        self.prepareGeometryChange()
        self.update()
        self.moved.emit()

    def paint(self, painter, option, widget):
        painter.setRenderHint(QPainter.Antialiasing)

        p1 = self.start.center()
        p2 = self.end.center()

        if self.isSelected():
            # Highlight underneath
            painter.setPen(QPen(self.highlightColor, 3))
            painter.drawLine(p1, p2)
            self.drawArrowHead(painter, p1, p2)

        # Normal edge on top
        painter.setPen(QPen(self.color, 1))
        painter.setBrush(QBrush(QColor(20, 20, 20)))
        painter.drawLine(p1, p2)
        self.drawArrowHead(painter, p1, p2)
        self.drawLabel(painter, p1, p2)

    def drawArrowHead(self, painter, start, end):
        dx = end.x() - start.x()
        dy = end.y() - start.y()

        angle = math.atan2(dy, dx)

        arrowLength = 10
        arrowWidth = 8

        # Desired centroid location
        centroid = QPointF(
            (start.x() + end.x()) / 2,
            (start.y() + end.y()) / 2,
        )

        # Unit direction vector
        ux = math.cos(angle)
        uy = math.sin(angle)

        # Tip is 2/3 of the length ahead of centroid
        tip = QPointF(
            centroid.x() + (2 * arrowLength / 3) * ux,
            centroid.y() + (2 * arrowLength / 3) * uy,
        )

        # Base center is 1/3 of the length behind centroid
        baseCenter = QPointF(
            centroid.x() - (arrowLength / 3) * ux,
            centroid.y() - (arrowLength / 3) * uy,
        )

        # Perpendicular vector
        px = -uy
        py = ux

        arrowPoint1 = QPointF(
            baseCenter.x() + (arrowWidth / 2) * px,
            baseCenter.y() + (arrowWidth / 2) * py,
        )

        arrowPoint2 = QPointF(
            baseCenter.x() - (arrowWidth / 2) * px,
            baseCenter.y() - (arrowWidth / 2) * py,
        )

        painter.drawPolygon(QPolygonF([tip, arrowPoint1, arrowPoint2]))

    def labelRect(self):
        if not self.label:
            return None

        p1 = self.start.center()
        p2 = self.end.center()

        dx = p2.x() - p1.x()
        dy = p2.y() - p1.y()

        length = math.hypot(dx, dy)
        if length < self.minLabelLength:
            return None

        ux = dx / length
        uy = dy / length

        # Midpoint
        mx = (p1.x() + p2.x()) * 0.5
        my = (p1.y() + p2.y()) * 0.5

        # Perpendicular offset
        offset = 12
        px = -uy
        py = ux

        pos = QPointF(
            mx + px * offset,
            my + py * offset,
        )

        metrics = QFontMetrics(QApplication.font())
        rect = metrics.boundingRect(self.label)
        rect.adjust(-4, -2, 4, 2)
        rect.moveCenter(pos.toPoint())

        return QRectF(rect)

    def drawLabel(self, painter, start, end):
        rect = self.labelRect()
        if rect is None:
            return

        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(20, 20, 20, 220))
        painter.drawRoundedRect(rect, 3, 3)

        painter.setPen(self.color)
        painter.drawText(rect, Qt.AlignCenter, self.label)

    def boundingRect(self):
        p1 = self.start.center()
        p2 = self.end.center()

        extra = 16

        rect = QRectF(
            min(p1.x(), p2.x()) - extra,
            min(p1.y(), p2.y()) - extra,
            abs(p2.x() - p1.x()) + 2 * extra,
            abs(p2.y() - p1.y()) + 2 * extra,
        )

        labelRect = self.labelRect()
        if labelRect is not None:
            rect = rect.united(labelRect)

        return rect

    def shape(self):
        p1 = self.start.center()
        p2 = self.end.center()

        path = QPainterPath()
        path.moveTo(p1)
        path.lineTo(p2)
        stroker = QPainterPathStroker()
        stroker.setWidth(16)

        return stroker.createStroke(path)

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        self.mousePressed.emit()
