import numpy as np
from PyQt5.QtCore import QPoint, QPointF, QRect, Qt, pyqtSignal
from PyQt5.QtGui import QBrush, QColor, QMouseEvent, QPainter, QPen, QRegion
from PyQt5.QtWidgets import QWidget


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


WORKSPACE_TRANSPARENCY = 10
WORKSPACE_DEFAULT_COLOR = QColor(255, 255, 255, WORKSPACE_TRANSPARENCY)
WORKSPACE_DEFAULT_BORDER = QColor(255, 255, 255, 255)


class ConfigurationHierarchy(dict):
    def __init__(self, config=None):
        super().__init__()
        self["config"] = config
        self["children"]: dict[str, ConfigurationHierarchy] = {}

    def setData(self, data):
        self["config"] = data["config"]
        children = data["children"]
        for c in children:
            config = ConfigurationHierarchy()
            config.setData(children[c])
            self.addChildConfig(c, config)

    def addChildConfig(self, name, config):
        if isinstance(config, ConfigurationHierarchy):
            self["children"][name] = config
        else:
            self["children"][name] = ConfigurationHierarchy(config)

    def getChildConfig(self, name):
        return self["children"][name]

    def children(self):
        return self["children"]

    def config(self):
        return self["config"]


class SelectionWindow(QWidget):
    resizeSignal = pyqtSignal()
    moveSignal = pyqtSignal()

    def __init__(self, name=None):
        super().__init__()
        self.name = name

        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.color = WORKSPACE_DEFAULT_COLOR
        self.borderColor = WORKSPACE_DEFAULT_BORDER

        super().setGeometry(500, 500, 500, 300)
        self.dragPosition = QPoint()
        self.resizeMode = False
        self.resizeIndices = None
        self.resizeError = (np.array([0.0, 0.0]), np.array([0.0, 0.0]))
        self.fixed = False

    def grabMouse(self) -> bool:
        if not self.canMove():
            return False
        self.setFocus()
        self.raise_()
        self.activateWindow()
        super().grabMouse()
        return True

    def mouseMoveEvent(self, event):
        if not self.canMove():
            return

        if not self.resizeMode:
            self.move(event.globalPos() - self.dragPosition)
            self.moveSignal.emit()
            return

        corners = self.getBBox()
        for i in self.resizeIndices:
            if i % 2 == 0:
                corners[i // 2].setX(event.globalPos().x())
            else:
                corners[i // 2].setY(event.globalPos().y())

        self.setGeometry(QRect(corners[0], corners[1]))
        self.resizeSignal.emit()

    def mousePressUpdate(self, event):
        self.dragPosition = event.globalPos() - self.frameGeometry().topLeft()

        threshold = 10
        dragx = self.dragPosition.x()
        dragy = self.dragPosition.y()
        sideActive = [
            0 <= dragx and dragx <= threshold,
            0 <= dragy and dragy <= threshold,
            self.width() - threshold <= dragx and dragx <= self.width(),
            self.height() - threshold <= dragy and dragy <= self.height(),
        ]
        activeCnt = [1 if v else 0 for v in sideActive]

        inX = 0 <= dragx and dragx <= self.width()
        inY = 0 <= dragy and dragy <= self.height()
        inside = inX and inY

        if not sum(activeCnt) or not inside or not self.canMove():
            if not inside:
                self.mouseReleaseEvent(event)
            self.resizeMode = False
        else:
            self.resizeMode = True
            self.resizeIndices = [i for i, x in enumerate(activeCnt) if x == 1]

    def mousePressEvent(self, event):
        self.mousePressUpdate(event)

        if self.canMove():
            self.grabMouse()

    def mouseReleaseEvent(self, event):
        self.releaseMouse()

    def resizeEvent(self, event):
        maskedRegion = QRegion(
            self.rect(),
            QRegion.RegionType.Rectangle,
        )
        self.setMask(maskedRegion)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        brush = QBrush(self.color)
        painter.setBrush(brush)

        pen = QPen(self.borderColor)
        painter.setPen(pen)

        rect = self.rect()
        painter.drawRect(rect.adjusted(2, 2, -2, -2))

        if self.name is not None:
            painter.setPen(QPen(QColor(255, 255, 255), 1))
            font = painter.font()
            font.setPointSize(12)
            font.setBold(True)
            painter.setFont(font)

            paddingTop = 10
            textRect = rect.adjusted(0, paddingTop, 0, 0)
            painter.drawText(textRect, Qt.AlignTop | Qt.AlignHCenter, self.name)

    def getBBox(self):
        return [
            self.frameGeometry().topLeft(),
            self.frameGeometry().bottomRight(),
        ]

    def setName(self, name):
        self.name = name
        self.repaint()

    def setColor(self, color, borderColor=WORKSPACE_DEFAULT_BORDER):
        self.color = color
        self.borderColor = borderColor
        self.repaint()

    def getColor(self):
        return self.color

    def lock(self):
        self.fixed = True

    def unlock(self):
        self.fixed = False

    def canMove(self):
        return not self.fixed


class Workspace(SelectionWindow):
    focusParent = pyqtSignal(QMouseEvent)
    mousePress = pyqtSignal()
    onDelete = pyqtSignal()

    def __init__(self, name=None):
        super().__init__(name)
        self.padding = 0
        self.wkspaces = []
        self.childFocused = None

    def isChild(self):
        return len(self.wkspaces) == 0

    def deleteLater(self):
        while len(self.wkspaces) > 0:
            self.wkspaces[0].deleteLater()

        self.onDelete.emit()
        super().deleteLater()

    def deleteChild(self, wks):
        self.wkspaces.pop(self.wkspaces.index(wks))
        if wks == self.childFocused:
            self.childFocused = None

    def addChild(self, wks):
        self.wkspaces.append(wks)
        wks.connectSignals(self.updateGeometry)
        wks.onDelete.connect(lambda: self.deleteChild(wks))
        wks.focusParent.connect(self.mousePressEvent)
        self.updateGeometry()

    def setChild(self, idx, wks):
        self.wkspaces[idx] = wks
        wks.connectSignals(self.updateGeometry)
        wks.onDelete.connect(lambda: self.deleteChild(wks))
        wks.focusParent.connect(self.mousePressEvent)
        self.updateGeometry()

    def childAt(self, idx):
        return self.wkspaces[idx]

    def removeChild(self, idx):
        wks = self.wkspaces[idx]
        self.wkspaces[idx] = None
        wks.disableSignals(self.updateGeometry)
        wks.focusParent.disconnect(self.mousePressEvent)
        self.updateGeometry()

    def setPadding(self, padding):
        self.padding = padding
        self.updateGeometry()

    def disableSignals(self, slot):
        self.resizeSignal.disconnect(slot)
        self.moveSignal.disconnect(slot)

    def connectSignals(self, slot):
        self.resizeSignal.connect(slot)
        self.moveSignal.connect(slot)

    def resize(self, newCorners):
        oldCorners = self.getBBox()

        # Account for padding
        oldCornersPadded = applyPadding(oldCorners, -self.padding)
        newCornersPadded = applyPadding(newCorners, -self.padding)

        # Get dimensions of old and new frame
        dimOld = oldCornersPadded[1] - oldCornersPadded[0]
        dimNew = newCornersPadded[1] - newCornersPadded[0]

        # Update child wkspace sizes resize displacement
        def childResize(wks):
            oldTl, oldBr = wks.getBBox()

            # linear interpolation
            s0 = (1.0 * oldTl.x() - oldCornersPadded[0].x()) / dimOld.x()
            t0 = (1.0 * oldTl.y() - oldCornersPadded[0].y()) / dimOld.y()
            s1 = (1.0 * oldBr.x() - oldCornersPadded[1].x()) / dimOld.x()
            t1 = (1.0 * oldBr.y() - oldCornersPadded[1].y()) / dimOld.y()

            prevTlErr, prevBrErr = wks.resizeError
            newTlx = dimNew.x() * s0 + newCornersPadded[0].x() + prevTlErr[0]
            newTly = dimNew.y() * t0 + newCornersPadded[0].y() + prevTlErr[1]
            newBrx = dimNew.x() * s1 + newCornersPadded[1].x() + prevBrErr[0]
            newBry = dimNew.y() * t1 + newCornersPadded[1].y() + prevBrErr[1]

            newTl = np.array([newTlx, newTly])
            newBr = np.array([newBrx, newBry])

            intNewTl = newTl.astype(int)
            intNewBr = newBr.astype(int)

            wks.resizeError = (newTl - intNewTl, newBr - intNewBr)

            newTl = QPoint(intNewTl[0], intNewTl[1])
            newBr = QPoint(intNewBr[0], intNewBr[1])

            wks.resize([newTl, newBr])

        for wks in self.wkspaces:
            childResize(wks)

        super().setGeometry(QRect(newCorners[0], newCorners[1]))
        self.resizeSignal.emit()

    def mouseMoveEvent(self, event):
        if self.childFocused is not None:
            self.releaseMouse()
            self.childFocused.grabMouse()
        else:
            if not self.canMove():
                return

            if self.resizeMode:
                newCorners = self.getBBox()

                # Compute displacement
                for i in self.resizeIndices:
                    if i % 2 == 0:
                        newCorners[i // 2].setX(event.globalPos().x())
                    else:
                        newCorners[i // 2].setY(event.globalPos().y())

                self.resize(newCorners)

            else:
                # Save prev state
                unlockState = []
                for w in self.wkspaces:
                    # No need to resize since children stick to layout
                    w.disableSignals(self.updateGeometry)
                    unlockState.append(w.canMove())
                    w.unlock()

                super().mouseMoveEvent(event)
                for wkspace in self.wkspaces:
                    wkspace.mouseMoveEvent(event)

                # Recover children state
                for i in range(len(self.wkspaces)):
                    # Reenable signals
                    w.connectSignals(self.updateGeometry)
                    w = self.wkspaces[i]
                    if not unlockState[i]:
                        w.lock()

    def grabMouse(self) -> bool:
        if not self.canMove():
            self.releaseMouse()
            return False

        if self.childFocused:
            self.childFocused.releaseMouse()
            self.childFocused = None

        self.setFocus()
        self.raise_()
        self.activateWindow()
        super().grabMouse()
        self.mousePress.emit()
        return True

    def releaseMouse(self):
        super().releaseMouse()
        for w in self.wkspaces:
            w.releaseMouse()

    def mousePressUpdate(self, event):
        super().mousePressUpdate(event)

        for wkspace in self.wkspaces:
            wkspace.mousePressUpdate(event)
            wkspace.mouseReleaseEvent(event)

    def mousePressEvent(self, event):
        self.mousePressUpdate(event)
        if self.childFocused:
            self.childFocused.mouseReleaseEvent(event)
            self.childFocused = None

        mousePos = event.globalPos()
        x = mousePos.x()
        y = mousePos.y()

        for i in range(len(self.wkspaces)):
            w = self.wkspaces[i]
            tl, br = w.getBBox()

            # Find child under mouse press
            if tl.x() < x and x < br.x():
                if tl.y() < y and y < br.y():
                    self.childFocused = w
                    success = w.grabMouse()
                    if success:
                        return

        success = self.grabMouse()
        if not success:
            self.focusParent.emit(event)

    def mouseReleaseEvent(self, event):
        if self.childFocused:
            self.childFocused.mouseReleaseEvent(event)
            self.childFocused = None
        self.releaseMouse()

    def updateGeometry(self):
        if len(self.wkspaces) != 0:
            tl, br = self.wkspaces[0].getBBox()
            tl, br = applyPadding((tl, br), self.padding)

            for wkspace in self.wkspaces:
                curTl, curBr = wkspace.getBBox()
                curTl, curBr = applyPadding((curTl, curBr), self.padding)

                tl.setX(min(tl.x(), curTl.x()))
                tl.setY(min(tl.y(), curTl.y()))
                br.setX(max(br.x(), curBr.x()))
                br.setY(max(br.y(), curBr.y()))

            super().setGeometry(QRect(tl, br))
        self.resizeSignal.emit()

    def setGeometry(self, rect):
        newTl, newBr = rect.topLeft(), rect.bottomRight()
        self.resize([newTl, newBr])
        self.resizeSignal.emit()

    def hide(self):
        super().hide()
        for wkspace in self.wkspaces:
            wkspace.hide()

    def show(self):
        super().show()
        for wkspace in self.wkspaces:
            wkspace.show()

    def lock(self):
        super().lock()
        for wkspace in self.wkspaces:
            wkspace.lock()

    def unlock(self):
        super().unlock()
        for wkspace in self.wkspaces:
            wkspace.unlock()


def exportData(wks: Workspace, extract_):
    data = dict(config=extract_(wks), children={})
    children = data["children"]
    for child in wks.wkspaces:
        children[child.id] = exportData(child, extract_)

    return data


def importData(wks: Workspace, data, import_):
    import_(wks, data["config"])
    children = data["children"]
    for child in wks.wkspaces:
        childData = children[child.id]
        importData(child, childData, import_)


def applyGeometry(wks, config):
    wks.setGeometry(layoutToBBox(config))


def extractGeometry(wks):
    return bboxToLayout(wks.getBBox())


def applyColor(wks, config):
    wks.setColor(listToColor(config))


def extractColor(wks):
    return colorToList(wks.getColor())
