from PyQt5.QtCore import QRect, QRectF, Qt
from PyQt5.QtGui import QColor, QPainter, QPen
from PyQt5.QtSvg import QSvgRenderer

from src.app.components.workspace.model import Color, Geometry, WorkspaceSchema

from .hierarchy import WindowHierarchy


class Workspace(WindowHierarchy):
    def __init__(self, name=None):
        super().__init__()
        self.name = name

        self.icon = None
        self.iconPath = None

    def setName(self, name: str):
        self.name = name
        self.repaint()

    def setIcon(self, svgPath):
        self.iconPath = svgPath
        self.icon = QSvgRenderer(svgPath)
        self.update()

    def unsetIcon(self):
        self.icon = None
        self.iconPath = None
        self.update()

    def getData(self) -> WorkspaceSchema:
        rect = self.geometry()
        return WorkspaceSchema(
            displayText=self.name,
            geometry=Geometry(
                x=rect.x(),
                y=rect.y(),
                width=rect.width(),
                height=rect.height(),
            ),
            iconPath=self.iconPath,
            padding=self.padding,
            color=Color(*self.color.getRgb()),
            borderColor=Color(*self.borderColor.getRgb()),
        )

    def setData(self, data: WorkspaceSchema):
        displayText = data.displayText
        rect = data.geometry
        iconPath = data.iconPath
        padding = data.padding
        color = data.color
        borderColor = data.borderColor

        if displayText is not None:
            self.setName(displayText)

        if padding is not None:
            self.setPadding(padding)

        if rect is not None:
            geometry = QRect(rect.x, rect.y, rect.width, rect.height)
            self.setGeometry(geometry)

        if iconPath is not None:
            if iconPath == "":
                self.unsetIcon()
            else:
                self.setIcon(iconPath)

        if color:
            color = QColor(color.r, color.g, color.b, color.a)

        if borderColor:
            borderColor = QColor(
                borderColor.r, borderColor.g, borderColor.b, borderColor.a
            )

        if color and borderColor:
            self.setColor(color, borderColor)

        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)

        rect = self.rect()
        if self.name is not None:
            painter.setPen(QPen(QColor(255, 255, 255), 1))
            font = painter.font()
            font.setPointSize(12)
            font.setBold(False)
            painter.setFont(font)

            paddingTop = 10
            textRect = rect.adjusted(0, paddingTop, 0, 0)
            painter.drawText(textRect, Qt.AlignTop | Qt.AlignHCenter, self.name)

        if self.icon:
            painter.setRenderHint(QPainter.Antialiasing)

            rect = self.rect()
            size = int(min(rect.width(), rect.height()) * 0.35)
            target = QRectF(
                rect.center().x() - size / 2,
                rect.center().y() - size / 2,
                size,
                size,
            )

            painter.save()
            painter.setOpacity(0.3)
            self.icon.render(painter, target)
            painter.restore()
        super().paintEvent(event)
