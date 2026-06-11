import numpy as np
from PyQt5.QtCore import QPoint, QRect, QRectF, pyqtSignal
from PyQt5.QtGui import QMouseEvent, QPainter
from PyQt5.QtSvg import QSvgRenderer

from .utils import applyPadding, bboxToLayout, layoutToBBox
from .window import SelectionWindow


class Workspace(SelectionWindow):
    focusParent = pyqtSignal(QMouseEvent)
    mousePress = pyqtSignal()
    onDelete = pyqtSignal()

    def __init__(self, name=None):
        super().__init__(name)
        self.padding = 0
        self.wkspaces = []
        self.childFocused = None

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

    def fitChildToCenter(self, wks, scale=0.7):
        tl, br = self.getBBox()
        tl, br = applyPadding((tl, br), self.padding)

        parentW = br.x() - tl.x()
        parentH = br.y() - tl.y()

        margin = 10
        parentW -= 2 * margin
        parentH -= 2 * margin

        childW = parentW * scale
        childH = parentH * scale

        cx = tl.x() + margin + parentW / 2
        cy = tl.y() + margin + parentH / 2

        newTl = QPoint(int(cx - childW / 2), int(cy - childH / 2))
        newBr = QPoint(int(cx + childW / 2), int(cy + childH / 2))

        wks.setGeometry(QRect(newTl, newBr))

    def addChild(self, wks):
        self.fitChildToCenter(wks)
        self.wkspaces.append(wks)
        wks.connectSignals(self.updateGeometry)
        wks.onDelete.connect(lambda: self.deleteChild(wks))
        wks.focusParent.connect(self.mousePressEvent)

    def setChild(self, idx, wks):
        self.fitChildToCenter(wks)
        self.wkspaces[idx] = wks
        wks.connectSignals(self.updateGeometry)
        wks.onDelete.connect(lambda: self.deleteChild(wks))
        wks.focusParent.connect(self.mousePressEvent)

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

    def restoreGeometry(self, rect):
        super().setGeometry(rect)

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
