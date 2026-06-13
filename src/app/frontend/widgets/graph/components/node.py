from dataclasses import dataclass
from typing import Optional

from PyQt5.QtCore import QPointF, QRectF, Qt
from PyQt5.QtGui import QBrush, QColor, QFont, QFontMetrics, QPen
from PyQt5.QtWidgets import QAbstractGraphicsShapeItem, QGraphicsItem

from src.app.frontend.state.layouts.graph import Color, Geometry

from .emitter import GraphicsEmitter


@dataclass
class NodeSchema:
    position: Optional[tuple[float, float]] = None
    color: Optional[Color] = None
    borderColor: Optional[Color] = None
    geometry: Optional[Geometry] = None
    displayText: Optional[str] = None


class NodeType:
    RECTANGLE = "Rectangle"
    CIRCLE = "Circle"


class GraphicsNode(QAbstractGraphicsShapeItem):
    def __init__(self, rect=QRectF(0, 0, 50, 50)):
        super().__init__()

        self._rect = QRectF(rect)

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

    def getData(self) -> NodeSchema:
        color = self.brush().color()
        bc = self.pen().color()
        rect = self.rect()

        return NodeSchema(
            position=(self.pos().x(), self.pos().y()),
            color=Color(*color.getRgb()),
            borderColor=Color(*bc.getRgb()),
            geometry=Geometry(
                x=rect.x(),
                y=rect.y(),
                width=rect.width(),
                height=rect.height(),
            ),
            displayText=self.displayText,
        )

    def setData(self, data: NodeSchema):
        position = data.position
        color = data.color
        borderColor = data.borderColor
        rect = data.geometry
        displayText = data.displayText

        if displayText is not None:
            self.displayText = displayText
            self.resizeToText()

        if color is not None:
            color = QColor(color.r, color.g, color.b, color.a)
            self.setBrush(QBrush(color))

        if borderColor is not None:
            color = QColor(borderColor.r, borderColor.g, borderColor.b, borderColor.a)
            pen = self.pen()
            pen.setColor(color)
            self.setPen(pen)

        if rect is not None:
            geometry = QRectF(rect.x, rect.y, rect.width, rect.height)
            self.setRect(geometry)

        if position:
            self.setPos(position[0], position[1])

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

    def drawShape(self, painter):
        raise NotImplementedError

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

            return nextPos

        elif change == QGraphicsItem.ItemPositionHasChanged:
            self.emitter.onMove_.emit(self.center())

        return super().itemChange(change, value)

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        self.emitter.onMousePress_.emit()


class GraphicsRectNode(GraphicsNode):
    def __init__(self, rect=QRectF(0, 0, 50, 50)):
        super().__init__(rect)

    def drawShape(self, painter, rect):
        painter.drawRect(rect)


class GraphicsCircleNode(GraphicsNode):
    def __init__(self, rect=QRectF(0, 0, 30, 30)):
        super().__init__(rect)

    def drawShape(self, painter, rect):
        painter.drawEllipse(rect)

    def resizeToText(self):
        pass
