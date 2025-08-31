import math

from PyQt5.QtCore import QObject, QPointF, QRectF, Qt, pyqtSignal
from PyQt5.QtGui import QBrush, QColor, QPainter, QPen, QPolygonF
from PyQt5.QtWidgets import QGraphicsItem, QGraphicsRectItem

NODE_DEFAULT_COLOR = QColor(20, 20, 20, 255)
NODE_HIGHLIGHT_COLOR = QColor(0, 163, 255, 255)


class GraphicsArrowItem(QGraphicsItem):
    def __init__(self, start: QPointF, end: QPointF):
        super().__init__()
        self.color = QColor(20, 20, 20, 255)
        self.end = QPointF(0, 0)
        self.setStart(start)
        self.setEnd(end)

    def setStart(self, start: QPointF):
        self.start = start
        v1 = self.start - self.end
        v2 = start - self.end

        a1 = math.atan2(v1.y(), v1.x())
        a2 = math.atan2(v2.y(), v2.x())

        self.setRotation(self.rotation() + a2 - a1)

    def setEnd(self, end: QPointF):
        self.end = end

        v1 = self.start - self.end
        v2 = self.start - end

        a1 = math.atan2(v1.y(), v1.x())
        a2 = math.atan2(v2.y(), v2.x())

        self.setRotation(self.rotation() + a2 - a1)

    def paint(self, painter, option, widget):
        painter.setRenderHint(QPainter.Antialiasing)
        brush = QBrush(self.color)
        painter.setBrush(brush)

        painter.drawLine(self.start, self.end)
        self.drawArrowHead(painter, self.start, self.end)

    def drawArrowHead(self, painter, start, end):
        lineDx = end.x() - start.x()
        lineDy = end.y() - start.y()

        angle = math.atan2(lineDy, lineDx)
        arrowSize = 10

        arrowPoint1 = QPointF(
            end.x() - arrowSize * math.cos(angle - math.pi / 6),
            end.y() - arrowSize * math.sin(angle - math.pi / 6),
        )
        arrowPoint2 = QPointF(
            end.x() - arrowSize * math.cos(angle + math.pi / 6),
            end.y() - arrowSize * math.sin(angle + math.pi / 6),
        )

        arrowhead = QPolygonF([end, arrowPoint1, arrowPoint2])
        painter.drawPolygon(arrowhead)

    def boundingRect(self):
        extra = 10
        xMin = min(self.start.x(), self.end.x()) - extra
        yMin = min(self.start.y(), self.end.y()) - extra
        xMax = max(self.start.x(), self.end.x()) + extra
        yMax = max(self.start.y(), self.end.y()) + extra

        return QRectF(xMin, yMin, xMax - xMin, yMax - yMin)


class GraphicsEmitter(QObject):
    onMove_ = pyqtSignal(QPointF)
    onMousePress_ = pyqtSignal()


class GraphicsNodeItem(QGraphicsRectItem):

    def __init__(self, rectF: QRectF, id: str):
        super().__init__(rectF)
        self.id = id
        self.displayText = None
        self.color = NODE_DEFAULT_COLOR
        self.highlightColor = NODE_HIGHLIGHT_COLOR
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)

        self.emitter = GraphicsEmitter()

    def setDisplayText(self, text):
        self.displayText = text
        self.update()

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        self.emitter.onMousePress_.emit()

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionChange:
            newPos = value

            sceneBounds = self.scene().sceneRect()
            itemBounds = self.mapRectToScene(self.rect())

            itemWidth = itemBounds.width()
            itemHeight = itemBounds.height()

            minX = sceneBounds.left()
            maxX = sceneBounds.right() - itemWidth
            minY = sceneBounds.top()
            maxY = sceneBounds.bottom() - itemHeight

            clampedX = max(minX, min(newPos.x(), maxX))
            clampedY = max(minY, min(newPos.y(), maxY))

            nextPos = QPointF(clampedX, clampedY)
            self.emitter.onMove_.emit(nextPos)

            return nextPos

        return super().itemChange(change, value)

    def paint(self, painter, option, widget):

        brush = QBrush(self.color)
        painter.setBrush(brush)

        rect = self.rect()
        painter.drawRect(rect)

        if self.isSelected():
            pen = QPen(self.highlightColor, 2)
            painter.setPen(pen)
            painter.drawRect(self.boundingRect())

        if self.displayText is not None:
            painter.setPen(QPen(QColor(255, 255, 255), 1))
            font = painter.font()
            font.setPointSize(12)
            font.setBold(True)
            painter.setFont(font)
            painter.drawText(rect, Qt.AlignVCenter | Qt.AlignHCenter, self.displayText)
