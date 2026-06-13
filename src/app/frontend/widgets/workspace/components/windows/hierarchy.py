from functools import partial

import numpy as np
from PyQt5.QtCore import QPoint, QRect, pyqtSignal
from PyQt5.QtGui import QMouseEvent

from .tracker import GeometryTracker
from .window import Window


class WindowHierarchy(Window):
    geometryUpdated = pyqtSignal()
    focusParent = pyqtSignal(QMouseEvent)
    onDelete = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.windows = []
        self.geometryTracker = GeometryTracker()

    def deleteLater(self):
        while len(self.windows) > 0:
            self.windows[0].deleteLater()

        self.onDelete.emit()
        super().deleteLater()

    def deleteChild(self, window):
        self.windows.pop(self.windows.index(window))

    def addChild(self, window):
        self.fitChildToCenter(window)

        self.windows.append(window)
        self.geometryTracker.addGeometry(window.geometry())

        id = len(self.windows) - 1
        updateGeometry = partial(self.updateChildTracker, id)
        resizeGeometry = partial(self.resizeFromChild, id)

        window.resizeSignal.connect(updateGeometry)
        window.resizeSignal.connect(resizeGeometry)

        window.moveSignal.connect(updateGeometry)
        window.moveSignal.connect(resizeGeometry)

        window.geometryUpdated.connect(updateGeometry)
        window.geometryUpdated.connect(self.updateGeometry)

        window.resizeDone.connect(self.onMovementFinish)
        window.moveDone.connect(self.onMovementFinish)

        window.onDelete.connect(lambda: self.deleteChild(window))
        window.focusParent.connect(self.mousePressEvent)

    def fitChildToCenter(self, window, scale=0.7):
        tl = self.geometry().topLeft()
        br = self.geometry().bottomRight()

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

        window.setGeometry(QRect(newTl, newBr))

    def resize(self, newRect):
        oldRect = self.geometry()

        # Consider inner frame
        newRect = newRect.adjusted(
            self.padding, self.padding, -self.padding, -self.padding
        )
        oldRect = oldRect.adjusted(
            self.padding, self.padding, -self.padding, -self.padding
        )

        # Get dimensions of old and new frame
        dimOld = oldRect.size()
        dimNew = newRect.size()

        # Update child window sizes resize displacement
        def childResize(window):
            oldTl = window.geometry().topLeft()
            oldBr = window.geometry().bottomRight()

            # linear interpolation
            s0 = (1.0 * oldTl.x() - oldRect.left()) / dimOld.width()
            t0 = (1.0 * oldTl.y() - oldRect.top()) / dimOld.height()
            s1 = (1.0 * oldBr.x() - oldRect.right()) / dimOld.width()
            t1 = (1.0 * oldBr.y() - oldRect.bottom()) / dimOld.height()

            prevTlErr, prevBrErr = window.resizeError
            newTlx = dimNew.width() * s0 + newRect.left() + prevTlErr[0]
            newTly = dimNew.height() * t0 + newRect.top() + prevTlErr[1]
            newBrx = dimNew.width() * s1 + newRect.right() + prevBrErr[0]
            newBry = dimNew.height() * t1 + newRect.bottom() + prevBrErr[1]

            newTl = np.array([newTlx, newTly])
            newBr = np.array([newBrx, newBry])

            intNewTl = newTl.astype(int)
            intNewBr = newBr.astype(int)

            window.resizeError = (newTl - intNewTl, newBr - intNewBr)

            newTl = QPoint(intNewTl[0], intNewTl[1])
            newBr = QPoint(intNewBr[0], intNewBr[1])

            window.resize(QRect(newTl, newBr))

        for window in self.windows:
            childResize(window)

        if not self.resizing:
            self.resizeBegin.emit()

        # Restore padding
        newRect = newRect.adjusted(
            -self.padding, -self.padding, self.padding, self.padding
        )
        super().setGeometry(newRect)
        self.resizing = True
        self.resizeSignal.emit()

    def mouseMoveEvent(self, event):
        if not self.canMove():
            return

        if self.resizeIndices:
            newRect = self.getResizeRect(event)
            self.resize(newRect)

        else:
            # Save prev state
            unlockState = []
            for i in range(len(self.windows)):
                w = self.windows[i]
                unlockState.append(w.canMove())
                w.unlock()

            super().mouseMoveEvent(event)
            for window in self.windows:
                window.mouseMoveEvent(event)

            # Recover children state
            for i in range(len(self.windows)):
                w = self.windows[i]
                if not unlockState[i]:
                    w.lock()

    def releaseMouse(self):
        super().releaseMouse()
        for w in self.windows:
            w.releaseMouse()

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        for w in self.windows:
            w.mouseReleaseEvent(event)

    def mousePressUpdate(self, event):
        super().mousePressUpdate(event)

        for window in self.windows:
            window.mousePressUpdate(event)

    def mousePressEvent(self, event):
        self.mousePressUpdate(event)

        mousePos = event.globalPos()
        x = mousePos.x()
        y = mousePos.y()

        for i in range(len(self.windows)):
            w = self.windows[i]
            if not w.canMove():
                continue

            tl = w.geometry().topLeft()
            br = w.geometry().bottomRight()

            # Find child under mouse press
            if tl.x() < x and x < br.x():
                if tl.y() < y and y < br.y():
                    w.mousePressEvent(event)
                    return

        if not self.canMove():
            self.focusParent.emit(event)
            return

        self.grabMouse()

    def updateChildTracker(self, idx):
        child = self.childAt(idx)
        self.geometryTracker.updateGeometry(idx, child.geometry())

    def updateGeometry(self):
        oldRect = self.geometry()
        newRect = self.geometryTracker.boundingBox()
        newRect = newRect.adjusted(
            -self.padding,
            -self.padding,
            self.padding,
            self.padding,
        )
        if oldRect != newRect:
            super().setGeometry(newRect)
            self.resizeSignal.emit()

    def resizeFromChild(self, idx):
        if self.moving:
            return

        oldRect = self.geometry()
        newRect = self.geometryTracker.boundingBox()
        newRect = newRect.adjusted(
            -self.padding,
            -self.padding,
            self.padding,
            self.padding,
        )
        if oldRect != newRect:
            if self.resizing:
                self.resizeBegin.emit()

            self.resizing = True
            super().setGeometry(newRect)
            self.resizeSignal.emit()

    def setGeometry(self, rect):
        super().setGeometry(rect)
        self.geometryUpdated.emit()

    def hide(self):
        super().hide()
        for window in self.windows:
            window.hide()

    def show(self):
        super().show()
        for window in self.windows:
            window.show()

    def lock(self):
        super().lock()
        for window in self.windows:
            window.lock()

    def unlock(self):
        super().unlock()
        for window in self.windows:
            window.unlock()

    def isChild(self):
        return len(self.windows) == 0

    def childAt(self, idx):
        return self.windows[idx]
