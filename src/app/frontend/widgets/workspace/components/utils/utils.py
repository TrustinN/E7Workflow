from PyQt5.QtCore import QPoint, QPointF, QRect
from PyQt5.QtGui import QColor


def qpointToList(point: QPointF):
    return [point.x(), point.y()]


def listToQPoint(arr):
    return QPointF(arr[0], arr[1])


def bboxToLayout(bbox):
    tl, br = bbox
    tlX, tlY = tl.x(), tl.y()
    brX, brY = br.x(), br.y()
    return [[tlX, tlY], [brX, brY]]


def applyPadding(bbox, padding):
    tl, br = bbox
    tlCpy = QPoint(tl.x(), tl.y())
    brCpy = QPoint(br.x(), br.y())
    tlCpy.setX(tlCpy.x() - padding)
    tlCpy.setY(tlCpy.y() - padding)
    brCpy.setX(brCpy.x() + padding)
    brCpy.setY(brCpy.y() + padding)
    return (tlCpy, brCpy)


def layoutToBBox(layout):
    tl, br = layout
    tl = QPoint(tl[0], tl[1])
    br = QPoint(br[0], br[1])
    return QRect(tl, br)


def colorToList(color):
    return [color.red(), color.green(), color.blue(), color.alpha()]


def listToColor(color):
    return QColor(*color)
