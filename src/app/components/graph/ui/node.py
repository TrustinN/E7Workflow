from PyQt5.QtCore import QPointF, QRectF, Qt
from PyQt5.QtGui import QBrush, QColor, QFont, QFontMetrics, QPen
from PyQt5.QtWidgets import QAbstractGraphicsShapeItem, QGraphicsItem

from .emitter import GraphicsEmitter


class NodeType:
    RECTANGLE = "Rectangle"
    CIRCLE = "Circle"


class GraphicsNode(QAbstractGraphicsShapeItem):
    def __init__(self, rect=QRectF(0, 0, 50, 50)):
        super().__init__()

        self._rect = QRectF(rect)
        self.shape = NodeType.RECTANGLE

        self.displayText = None
        self.highlightColor = QColor(0, 163, 255)

        self.setBrush(QBrush(QColor(20, 20, 20)))
        self.setPen(QPen(QColor(255, 255, 255), 1))

        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        self.setFlag(QGraphicsItem.ItemIsSelectable)

        self.emitter = GraphicsEmitter()

    def rect(self):
        return QRectF(self._rect)

    def setRect(self, rect):
        self.prepareGeometryChange()
        self._rect = QRectF(rect)
        self.update()

    def boundingRect(self):
        return self._rect.adjusted(-2, -2, 2, 2)

    def getData(self) -> dict:
        color = self.brush().color()
        bc = self.pen().color()
        rect = self.rect()

        return {
            "position": (self.pos().x(), self.pos().y()),
            "color": list(color.getRgb()),
            "borderColor": list(bc.getRgb()),
            "geometry": [
                rect.x(),
                rect.y(),
                rect.width(),
                rect.height(),
            ],
            "shape": self.shape,
            "displayText": self.displayText,
            "visible": self.isVisible(),
        }

    def setData(self, data: dict):
        position = data.get("position")
        color = data.get("color")
        borderColor = data.get("borderColor")
        rect = data.get("geometry")
        shape = data.get("shape")
        displayText = data.get("displayText")
        visible = data.get("visible")

        if displayText is not None:
            self.displayText = displayText
            self.resizeToText()

        if color is not None:
            color = QColor(*color)
            self.setBrush(QBrush(color))

        if borderColor is not None:
            borderColor = QColor(*borderColor)
            pen = self.pen()
            pen.setColor(borderColor)
            self.setPen(pen)

        if rect is not None:
            geometry = QRectF(*rect)
            self.setRect(geometry)

        if position:
            self.setPos(position[0], position[1])

        if shape:
            self.shape = shape

        if visible is not None:
            self.setVisible(visible)

        self.update()

    def center(self):
        return self.mapToScene(self._rect.center())

    def resizeToText(self):
        if not self.displayText:
            return

        font = QFont()
        font.setPointSize(12)
        font.setBold(True)

        metrics = QFontMetrics(font)

        width = max(
            50,
            metrics.horizontalAdvance(self.displayText) + 20,
        )

        self.setRect(
            QRectF(
                self._rect.x(),
                self._rect.y(),
                width,
                self._rect.height(),
            )
        )

    def drawShape(self, painter, rect):
        if self.shape == NodeType.RECTANGLE:
            painter.drawRect(rect)
        elif self.shape == NodeType.CIRCLE:
            painter.drawEllipse(rect)

    def paint(self, painter, option, widget):
        painter.setPen(self.pen())
        painter.setBrush(self.brush())
        self.drawShape(painter, self.rect().adjusted(2, 2, -2, -2))

        if self.isSelected():
            painter.setPen(QPen(self.highlightColor, 2))
            painter.setBrush(Qt.NoBrush)
            self.drawShape(painter, self.rect())

        if self.displayText:
            painter.setPen(Qt.white)

            font = painter.font()
            font.setPointSize(12)
            font.setBold(True)
            painter.setFont(font)

            painter.drawText(
                self._rect,
                Qt.AlignCenter,
                self.displayText,
            )

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

            self.emitter.onMove.emit()
            return nextPos

        return super().itemChange(change, value)

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        self.emitter.onMousePress.emit()
