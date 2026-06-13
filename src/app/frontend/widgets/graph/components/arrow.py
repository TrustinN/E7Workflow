import math
from dataclasses import dataclass
from typing import Optional

from PyQt5.QtCore import QPointF, QRectF
from PyQt5.QtGui import QBrush, QColor, QPainter, QPolygonF
from PyQt5.QtWidgets import QGraphicsItem

from .emitter import GraphicsEmitter


@dataclass
class EdgeSchema:
    start: Optional[str] = None
    end: Optional[str] = None


class GraphicsArrowItem(QGraphicsItem):
    def __init__(
        self,
        start: QPointF = QPointF(0, 0),
        end: QPointF = QPointF(1, 1),
    ):
        super().__init__()
        self.color = QColor(20, 20, 20, 255)
        self.end = QPointF(0, 0)
        self.emitter = GraphicsEmitter()

        self.setZValue(-1)
        self.setStart(start)
        self.setEnd(end)

    def getData(self) -> EdgeSchema:
        return EdgeSchema()

    def setStart(self, start: QPointF):
        self.start = start
        v1 = self.start - self.end
        v2 = start - self.end

        a1 = math.atan2(v1.y(), v1.x())
        a2 = math.atan2(v2.y(), v2.x())

        self.setRotation(self.rotation() + a2 - a1)
        self.update()

        self.emitter.onMove_.emit(self.start)

    def setEnd(self, end: QPointF):
        self.end = end

        v1 = self.start - self.end
        v2 = self.start - end

        a1 = math.atan2(v1.y(), v1.x())
        a2 = math.atan2(v2.y(), v2.x())

        self.setRotation(self.rotation() + a2 - a1)
        self.update()

        self.emitter.onMove_.emit(self.end)

    def paint(self, painter, option, widget):
        painter.setRenderHint(QPainter.Antialiasing)
        brush = QBrush(self.color)
        painter.setBrush(brush)

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
