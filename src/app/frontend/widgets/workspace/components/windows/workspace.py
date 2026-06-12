from PyQt5.QtCore import QRectF
from PyQt5.QtGui import QPainter
from PyQt5.QtSvg import QSvgRenderer

from .hierarchy import WindowHierarchy
from .utils import bboxToLayout, layoutToBBox


class Workspace(WindowHierarchy):
    def __init__(self, name=None):
        super().__init__(name)
        self.icon = None
        self.iconPath = None

    def setIcon(self, svgPath):
        if svgPath == "":
            self.icon = None
            self.iconPath = None
            return

        self.iconPath = svgPath
        self.icon = QSvgRenderer(svgPath)
        self.update()

    def getData(self):
        return {
            "padding": self.padding,
            "text": self.name,
            "geometry": bboxToLayout(self.getBBox()),
            "iconPath": self.iconPath,
        }

    def setData(self, data):
        padding = data.get("padding")
        text = data.get("text")
        geometry = data.get("geometry")
        iconPath = data.get("iconPath")

        if padding is not None:
            self.padding = padding

        if text is not None:
            self.name = text

        if geometry is not None:
            self.setGeometry(layoutToBBox(geometry))

        if iconPath is not None:
            self.setIcon(iconPath)

        self.update()

    def paintEvent(self, event):
        if self.icon:
            painter = QPainter(self)
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
