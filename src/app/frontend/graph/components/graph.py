import math

from PyQt5.QtCore import QObject, QPointF, QRectF, Qt, pyqtSignal
from PyQt5.QtGui import QBrush, QColor, QPainter, QPen, QPolygonF
from PyQt5.QtWidgets import QGraphicsItem, QGraphicsRectItem, QGraphicsScene

NODE_DEFAULT_COLOR = QColor(20, 20, 20, 255)
NODE_HIGHLIGHT_COLOR = QColor(0, 163, 255, 255)


class GraphicsEmitter(QObject):
    onMove_ = pyqtSignal(QPointF)
    onMousePress_ = pyqtSignal()


class GraphicsArrowItem(QGraphicsItem):
    def __init__(
        self,
        start: QPointF = QPointF(0, 0),
        end: QPointF = QPointF(1, 1),
    ):
        super().__init__()
        self.color = QColor(20, 20, 20, 255)
        self.end = QPointF(0, 0)
        self.setStart(start)
        self.setEnd(end)

    def getData(self):
        return {
            "startPosition": [self.start.x(), self.start.y()],
            "endPosition": [self.end.x(), self.end.y()],
        }

    def setData(self, data):
        startPosition = data.get("startPosition")
        endPosition = data.get("endPosition")

        if startPosition is not None:
            self.setStart(QPointF(*startPosition))

        if endPosition is not None:
            self.setEnd(QPointF(*endPosition))

    def setStart(self, start: QPointF):
        self.start = start
        v1 = self.start - self.end
        v2 = start - self.end

        a1 = math.atan2(v1.y(), v1.x())
        a2 = math.atan2(v2.y(), v2.x())

        self.setRotation(self.rotation() + a2 - a1)
        self.update()

    def setEnd(self, end: QPointF):
        self.end = end

        v1 = self.start - self.end
        v2 = self.start - end

        a1 = math.atan2(v1.y(), v1.x())
        a2 = math.atan2(v2.y(), v2.x())

        self.setRotation(self.rotation() + a2 - a1)
        self.update()

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


class GraphicsNodeItem(QGraphicsRectItem):

    def __init__(self, rectF: QRectF = QRectF(0, 0, 50, 50)):
        super().__init__(rectF)
        self.displayText = None
        self.color = NODE_DEFAULT_COLOR
        self.highlightColor = NODE_HIGHLIGHT_COLOR
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)

        self.emitter = GraphicsEmitter()

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


class NodeType:
    DEFAULT = 0
    LOCAL_ENTRYPOINT = 1
    GLOBAL_ENTRYPOINT = 2


class NodeState:
    DEFAULT = 0
    MARKED = 1


class WorkspaceNodeItem(GraphicsNodeItem):
    def __init__(self, rectF, id):
        super().__init__(rectF, id)
        self.type_ = None
        self.state_ = None

    def setType(self, nodeType):
        self.type_ = nodeType
        super().update()

    def setState(self, nodeState):
        self.state_ = nodeState
        super().update()

    def paint(self, painter, option, widget):
        super().paint(painter, option, widget)
        self.paintNodeType(painter, option, widget)
        self.paintNodeState(painter, option, widget)

    def paintNodeType(self, painter, option, widget):
        match self.type_:
            case NodeType.LOCAL_ENTRYPOINT | NodeType.GLOBAL_ENTRYPOINT:
                rect = self.boundingRect()
                w, h = rect.width(), rect.height()

                # arrow size
                base = min(w, h) * 0.12  # base width
                length = min(w, h) * 0.18  # arrow length inward

                color = QColor(144, 238, 144)
                if self.type_ == NodeType.GLOBAL_ENTRYPOINT:
                    color = QColor(200, 160, 255)
                painter.setBrush(QBrush(color))  # mellow green
                painter.setPen(Qt.NoPen)

                # Top-left corner (points toward center)
                painter.drawPolygon(
                    QPolygonF(
                        [
                            QPointF(rect.left(), rect.top() + length),
                            QPointF(rect.left() + base, rect.top()),
                            QPointF(rect.left(), rect.top()),
                        ]
                    )
                )

                # Top-right corner
                painter.drawPolygon(
                    QPolygonF(
                        [
                            QPointF(rect.right(), rect.top() + length),
                            QPointF(rect.right() - base, rect.top()),
                            QPointF(rect.right(), rect.top()),
                        ]
                    )
                )

                # Bottom-left corner
                painter.drawPolygon(
                    QPolygonF(
                        [
                            QPointF(rect.left(), rect.bottom() - length),
                            QPointF(rect.left() + base, rect.bottom()),
                            QPointF(rect.left(), rect.bottom()),
                        ]
                    )
                )

                # Bottom-right corner
                painter.drawPolygon(
                    QPolygonF(
                        [
                            QPointF(rect.right(), rect.bottom() - length),
                            QPointF(rect.right() - base, rect.bottom()),
                            QPointF(rect.right(), rect.bottom()),
                        ]
                    )
                )
            case NodeType.DEFAULT:
                pass

    def paintNodeState(self, painter, option, widget):
        match self.state_:
            case NodeState.MARKED:
                rect = self.boundingRect()
                w, h = rect.width(), rect.height()

                # corner bracket size
                bracket_len = min(w, h) * 0.2
                pen = QPen(QColor(255, 0, 0))  # red
                pen.setWidth(2)
                painter.setPen(pen)

                # Top-left
                painter.drawLine(
                    rect.topLeft(), rect.topLeft() + QPointF(bracket_len, 0)
                )  # horizontal
                painter.drawLine(
                    rect.topLeft(), rect.topLeft() + QPointF(0, bracket_len)
                )  # vertical

                # Top-right
                painter.drawLine(
                    rect.topRight(), rect.topRight() - QPointF(bracket_len, 0)
                )
                painter.drawLine(
                    rect.topRight(), rect.topRight() + QPointF(0, bracket_len)
                )

                # Bottom-left
                painter.drawLine(
                    rect.bottomLeft(), rect.bottomLeft() + QPointF(bracket_len, 0)
                )
                painter.drawLine(
                    rect.bottomLeft(), rect.bottomLeft() - QPointF(0, bracket_len)
                )

                # Bottom-right
                painter.drawLine(
                    rect.bottomRight(), rect.bottomRight() - QPointF(bracket_len, 0)
                )
                painter.drawLine(
                    rect.bottomRight(), rect.bottomRight() - QPointF(0, bracket_len)
                )


class InteractiveGraphScene(QGraphicsScene):
    itemSelected_ = pyqtSignal(object)

    def __init__(self):
        super().__init__()
        self.setSceneRect(0, 0, 400, 300)

        self.selectionChanged.connect(
            lambda: self.itemSelected_.emit(self.getSelection())
        )

    def getSelection(self):
        selected = self.selectedItems()
        if selected:
            item = selected[0]
            return item

        return None
