from PyQt5.QtCore import QPointF, Qt
from PyQt5.QtGui import QBrush, QColor, QPen, QPolygonF

from .node import GraphicsNodeItem


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
