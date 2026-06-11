from PyQt5.QtCore import QObject, QPointF, QRectF, Qt, pyqtSignal
from PyQt5.QtGui import QBrush, QColor, QFont, QFontMetrics, QPen
from PyQt5.QtWidgets import (
    QAbstractGraphicsShapeItem,
    QGraphicsEllipseItem,
    QGraphicsItem,
    QGraphicsRectItem,
)

NODE_DEFAULT_COLOR = QColor(20, 20, 20, 255)
NODE_DEFAULT_BORDER = QColor(255, 255, 255, 255)
NODE_HIGHLIGHT_COLOR = QColor(0, 163, 255, 255)


class NodeType:
    RECTANGLE = "Rectangle"
    CIRCLE = "Circle"


NODE_DEFAULT_COLOR = QColor(20, 20, 20)
NODE_DEFAULT_BORDER = QColor(255, 255, 255)
NODE_HIGHLIGHT_COLOR = QColor(0, 163, 255)


class GraphicsEmitter(QObject):
    onMove_ = pyqtSignal(QPointF)
    onMousePress_ = pyqtSignal()


class GraphicsNode(QAbstractGraphicsShapeItem):
    def __init__(self, rect=QRectF(0, 0, 50, 50)):
        super().__init__()

        self._rect = QRectF(rect)

        self.displayText = None
        self.highlightColor = NODE_HIGHLIGHT_COLOR

        self.setBrush(QBrush(NODE_DEFAULT_COLOR))
        self.setPen(QPen(NODE_DEFAULT_BORDER, 1))

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

    def setGeometry(self, rect):
        self.setRect(QRectF(*rect))

    def getGeometry(self):
        r = self._rect
        return [r.x(), r.y(), r.width(), r.height()]

    def setPosition(self, position):
        self.setPos(QPointF(*position))

    def getPosition(self):
        pos = self.pos()
        return [pos.x(), pos.y()]

    def getColor(self):
        color = self.brush().color()
        return [
            color.red(),
            color.green(),
            color.blue(),
        ]

    def setColor(self, color):
        self.setBrush(QBrush(QColor(*color)))

    def getData(self):
        bc = self.pen().color()

        return {
            "position": self.getPosition(),
            "color": self.getColor(),
            "borderColor": [
                bc.red(),
                bc.green(),
                bc.blue(),
            ],
            "rect": self.getGeometry(),
            "displayText": self.displayText,
        }

    def setData(self, data):
        position = data.get("position")
        color = data.get("color")
        borderColor = data.get("borderColor")
        rect = data.get("rect")
        displayText = data.get("displayText")

        if position is not None:
            self.setPosition(position)

        if color is not None:
            self.setColor(color)

        if borderColor is not None:
            pen = self.pen()
            pen.setColor(QColor(*borderColor))
            self.setPen(pen)

        if rect is not None:
            self.setGeometry(rect)

        if displayText is not None:
            self.displayText = displayText
            self.resizeToText()

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
