from functools import partial

import numpy as np
from PyQt5.QtCore import QPoint, QRect, pyqtSignal
from PyQt5.QtGui import QMouseEvent

from .tracker import GeometryTracker
from .utils import applyPadding
from .window import Window


class WindowHierarchy(Window):
    updateGeometry = pyqtSignal()
    focusParent = pyqtSignal(QMouseEvent)
    onDelete = pyqtSignal()

    def __init__(self, name=None):
        super().__init__(name)
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
        updateGeometry = partial(self.updateGeometryFromChild, id)
        resizeGeometry = partial(self.resizeFromChild, id)

        window.resizeSignal.connect(updateGeometry)
        window.resizeSignal.connect(resizeGeometry)

        window.moveSignal.connect(updateGeometry)
        window.moveSignal.connect(resizeGeometry)

        window.updateGeometry.connect(updateGeometry)

        window.resizeDone.connect(self.onMovementFinish)
        window.moveDone.connect(self.onMovementFinish)

        window.onDelete.connect(lambda: self.deleteChild(window))
        window.focusParent.connect(self.mousePressEvent)

    def fitChildToCenter(self, window, scale=0.7):
        tl, br = self.getBBox()

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

    def resize(self, newCorners):
        oldCorners = self.getBBox()

        # Account for padding
        oldCornersPadded = applyPadding(oldCorners, -self.padding)
        newCornersPadded = applyPadding(newCorners, -self.padding)

        # Get dimensions of old and new frame
        dimOld = oldCornersPadded[1] - oldCornersPadded[0]
        dimNew = newCornersPadded[1] - newCornersPadded[0]

        # Update child window sizes resize displacement
        def childResize(window):
            oldTl, oldBr = window.getBBox()

            # linear interpolation
            s0 = (1.0 * oldTl.x() - oldCornersPadded[0].x()) / dimOld.x()
            t0 = (1.0 * oldTl.y() - oldCornersPadded[0].y()) / dimOld.y()
            s1 = (1.0 * oldBr.x() - oldCornersPadded[1].x()) / dimOld.x()
            t1 = (1.0 * oldBr.y() - oldCornersPadded[1].y()) / dimOld.y()

            prevTlErr, prevBrErr = window.resizeError
            newTlx = dimNew.x() * s0 + newCornersPadded[0].x() + prevTlErr[0]
            newTly = dimNew.y() * t0 + newCornersPadded[0].y() + prevTlErr[1]
            newBrx = dimNew.x() * s1 + newCornersPadded[1].x() + prevBrErr[0]
            newBry = dimNew.y() * t1 + newCornersPadded[1].y() + prevBrErr[1]

            newTl = np.array([newTlx, newTly])
            newBr = np.array([newBrx, newBry])

            intNewTl = newTl.astype(int)
            intNewBr = newBr.astype(int)

            window.resizeError = (newTl - intNewTl, newBr - intNewBr)

            newTl = QPoint(intNewTl[0], intNewTl[1])
            newBr = QPoint(intNewBr[0], intNewBr[1])

            window.resize([newTl, newBr])

        for window in self.windows:
            childResize(window)

        if not self.resizing:
            self.resizeBegin.emit()

        super().setGeometry(QRect(newCorners[0], newCorners[1]))
        self.resizing = True
        self.resizeSignal.emit()

    def mouseMoveEvent(self, event):
        if not self.canMove():
            return

        if self.resizeIndices:
            newCorners = self.getResizeCorners(event)
            self.resize(newCorners)

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

            tl, br = w.getBBox()

            # Find child under mouse press
            if tl.x() < x and x < br.x():
                if tl.y() < y and y < br.y():
                    w.mousePressEvent(event)
                    return

        if not self.canMove():
            self.focusParent.emit(event)
            return

        self.grabMouse()

    def updateGeometryFromChild(self, idx):
        child = self.childAt(idx)
        self.geometryTracker.updateGeometry(idx, child.geometry())

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
        self.updateGeometry.emit()

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
