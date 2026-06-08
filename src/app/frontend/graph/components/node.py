from PyQt5.QtCore import QObject, QPointF, QRectF, Qt, pyqtSignal
from PyQt5.QtGui import QBrush, QColor, QFont, QFontMetrics, QPen
from PyQt5.QtWidgets import QGraphicsEllipseItem, QGraphicsItem, QGraphicsRectItem

NODE_DEFAULT_COLOR = QColor(20, 20, 20, 255)
NODE_HIGHLIGHT_COLOR = QColor(0, 163, 255, 255)


class NodeType:
    RECTANGLE = "Rectangle"
    CIRCLE = "Circle"


class GraphicsEmitter(QObject):
    onMove_ = pyqtSignal(QPointF)
    onMousePress_ = pyqtSignal()


class GraphicsNode:
    def __init__(self):
        self.displayText = None
        self.color = NODE_DEFAULT_COLOR
        self.highlightColor = NODE_HIGHLIGHT_COLOR
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)

        self.emitter = GraphicsEmitter()

    def center(self):
        return self.mapToScene(self.rect().center())

    def getData(self):
        return

    def setData(self, data):
        return


class GraphicsRectNode(QGraphicsRectItem, GraphicsNode):

    def __init__(self, rectF: QRectF = QRectF(0, 0, 50, 50)):
        QGraphicsRectItem.__init__(self, rectF)
        GraphicsNode.__init__(self)

    def getData(self):
        pos = self.pos()
        r = self.rect()
        c = self.color
        return {
            "position": [pos.x(), pos.y()],
            "color": [c.red(), c.green(), c.blue()],
            "rect": [r.x(), r.y(), r.width(), r.height()],
            "displayText": self.displayText,
        }

    def setData(self, data):
        position = data.get("position")
        color = data.get("color")
        rect = data.get("rect")
        displayText = data.get("displayText")

        if position is not None:
            self.setPos(QPointF(*position))

        if color is not None:
            self.color = QColor(*color)

        if rect is not None:
            self.setRect(QRectF(*rect))

        if displayText is not None:
            self.displayText = displayText
            self.resizeToText()

        self.update()

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        self.emitter.onMousePress_.emit()

    def resizeToText(self):
        if not self.displayText:
            return

        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        metrics = QFontMetrics(font)
        padding = 20
        minWidth = 50
        width = max(minWidth, metrics.horizontalAdvance(self.displayText) + padding)
        rect = self.rect()
        self.setRect(rect.x(), rect.y(), width, rect.height())
        self.clampToScene()

    def clampToScene(self):
        scene = self.scene()
        if scene is None:
            return

        sceneRect = scene.sceneRect()
        rect = self.sceneBoundingRect()

        x = self.pos().x()
        y = self.pos().y()

        if rect.right() > sceneRect.right():
            x -= rect.right() - sceneRect.right()

        if rect.left() < sceneRect.left():
            x += sceneRect.left() - rect.left()

        if rect.bottom() > sceneRect.bottom():
            y -= rect.bottom() - sceneRect.bottom()

        if rect.top() < sceneRect.top():
            y += sceneRect.top() - rect.top()

        self.setPos(x, y)

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


class GraphicsCircleNode(QGraphicsEllipseItem, GraphicsNode):
    def __init__(self, rectF: QRectF = QRectF(0, 0, 25, 25)):
        QGraphicsEllipseItem.__init__(self, rectF)
        GraphicsNode.__init__(self)

    def getData(self):
        pos = self.pos()
        r = self.rect()
        c = self.color
        return {
            "position": [pos.x(), pos.y()],
            "color": [c.red(), c.green(), c.blue()],
            "rect": [r.x(), r.y(), r.width(), r.height()],
            "displayText": self.displayText,
        }

    def setData(self, data):
        position = data.get("position")
        color = data.get("color")
        rect = data.get("rect")
        displayText = data.get("displayText")
        if position is not None:
            self.setPos(QPointF(*position))

        if color is not None:
            self.color = QColor(*color)

        if rect is not None:
            self.setRect(QRectF(*rect))

        if displayText is not None:
            self.displayText = displayText

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

            return QPointF(clampedX, clampedY)

        elif change == QGraphicsItem.ItemPositionHasChanged:
            self.emitter.onMove_.emit(self.center())

        return super().itemChange(change, value)

    def paint(self, painter, option, widget):
        rect = self.rect()

        painter.setBrush(QBrush(self.color))
        painter.setPen(QPen(QColor(255, 255, 255), 1))
        painter.drawEllipse(rect)

        if self.isSelected():
            painter.setPen(QPen(self.highlightColor, 2))
            painter.setBrush(Qt.NoBrush)
            painter.drawEllipse(self.boundingRect())

        if self.displayText is not None:
            painter.setPen(QPen(QColor(255, 255, 255), 1))

            font = painter.font()
            font.setPointSize(12)
            font.setBold(True)
            painter.setFont(font)

            painter.drawText(
                rect,
                Qt.AlignCenter,
                self.displayText,
            )
