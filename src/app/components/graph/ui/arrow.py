import math

from PyQt5.QtCore import QPointF, QRectF
from PyQt5.QtGui import (
    QBrush,
    QColor,
    QPainter,
    QPainterPath,
    QPainterPathStroker,
    QPen,
    QPolygonF,
)
from PyQt5.QtWidgets import QGraphicsItem

from .emitter import GraphicsEmitter


class GraphicsArrowItem(QGraphicsItem):
    def __init__(self):
        super().__init__()
        self.color = QColor(255, 255, 255)
        self.highlightColor = QColor(0, 163, 255)
        self.emitter = GraphicsEmitter()

        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setZValue(-1)

    def getData(self) -> dict:
        return {
            "visible": self.isVisible(),
        }

    def setData(self, data) -> dict:
        visible = data.get("visible")

        if visible is not None:
            self.setVisible(visible)

    def setPosition(self, start: QPointF, end: QPointF):
        self.prepareGeometryChange()
        self.start = start
        self.end = end
        self.update()

    def setStart(self, start: QPointF):
        self.prepareGeometryChange()
        self.start = start
        self.update()
        self.emitter.onMove.emit()

    def setEnd(self, end: QPointF):
        self.prepareGeometryChange()
        self.end = end
        self.update()
        self.emitter.onMove.emit()

    def paint(self, painter, option, widget):
        painter.setRenderHint(QPainter.Antialiasing)

        if not (self.start and self.end):
            return

        if self.isSelected():
            # Highlight underneath
            painter.setPen(QPen(self.highlightColor, 3))
            painter.drawLine(self.start, self.end)
            self.drawArrowHead(painter, self.start, self.end)

        # Normal edge on top
        painter.setPen(QPen(self.color, 1))
        painter.setBrush(QBrush(QColor(20, 20, 20)))
        painter.drawLine(self.start, self.end)
        self.drawArrowHead(painter, self.start, self.end)

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

    def boundingRect(self):
        extra = 10
        xMin = min(self.start.x(), self.end.x()) - extra
        yMin = min(self.start.y(), self.end.y()) - extra
        xMax = max(self.start.x(), self.end.x()) + extra
        yMax = max(self.start.y(), self.end.y()) + extra

        return QRectF(xMin, yMin, xMax - xMin, yMax - yMin)

    def shape(self):
        path = QPainterPath()
        path.moveTo(self.start)
        path.lineTo(self.end)
        stroker = QPainterPathStroker()
        stroker.setWidth(16)

        return stroker.createStroke(path)

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        self.emitter.onMousePress.emit()
