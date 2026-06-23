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
from .node import GraphicsNode


class GraphicsArrowItem(QGraphicsItem):
    def __init__(self, start: GraphicsNode, end: GraphicsNode):
        super().__init__()
        self.color = QColor(255, 255, 255)
        self.highlightColor = QColor(0, 163, 255)
        self.emitter = GraphicsEmitter()

        self.start = start
        self.start.emitter.onMove.connect(self.onNodeMove)

        self.end = end
        self.end.emitter.onMove.connect(self.onNodeMove)

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

    def onNodeMove(self):
        self.prepareGeometryChange()
        self.update()
        self.emitter.onMove.emit()

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
        p1 = self.start.center()
        p2 = self.end.center()

        extra = 10
        xMin = min(p1.x(), p2.x()) - extra
        yMin = min(p1.y(), p2.y()) - extra
        xMax = max(p1.x(), p2.x()) + extra
        yMax = max(p1.y(), p2.y()) + extra

        return QRectF(xMin, yMin, xMax - xMin, yMax - yMin)

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
        self.emitter.onMousePress.emit()
