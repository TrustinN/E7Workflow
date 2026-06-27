from functools import partial

import numpy as np
from PyQt5.QtCore import QPoint, QRect, pyqtSignal
from PyQt5.QtGui import QMouseEvent

from .tracker import GeometryTracker
from .window import Window


class WindowHierarchy(Window):
    childAdded = pyqtSignal()
    geometryUpdated = pyqtSignal()
    focusParent = pyqtSignal(QMouseEvent)
    onDelete = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.windows = {}
        self.geometryTracker = GeometryTracker()

    def deleteLater(self):
        for id, window in list(self.windows.items()):
            window.deleteLater()

        self.windows.clear()
        self.onDelete.emit()
        super().deleteLater()

    def deleteChild(self, id):
        self.windows.pop(id)
        self.geometryTracker.removeGeometry(id)
        self.resizeFromChild()

    def addChild(self, id, window):

        self.windows[id] = window
        self.geometryTracker.addGeometry(id, window.geometry())

        updateGeometry = partial(self.updateChildTracker, id)
        resizeGeometry = self.resizeFromChild

        window.resizeSignal.connect(updateGeometry)
        window.resizeSignal.connect(resizeGeometry)

        window.moveSignal.connect(updateGeometry)
        window.moveSignal.connect(resizeGeometry)

        window.geometryUpdated.connect(updateGeometry)
        window.geometryUpdated.connect(self.updateGeometry)

        window.resizeDone.connect(self.onMovementFinish)
        window.moveDone.connect(self.onMovementFinish)

        window.onDelete.connect(lambda: self.deleteChild(id))
        window.focusParent.connect(self.mousePressEvent)

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

        for window in self.windows.values():
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
            unlockState = {}
            for id, w in self.windows.items():
                unlockState[id] = w.canMove()
                w.unlock()

            super().mouseMoveEvent(event)
            for window in self.windows.values():
                window.mouseMoveEvent(event)

            # Recover children state
            for id, w in self.windows.items():
                if not unlockState[id]:
                    w.lock()

    def releaseMouse(self):
        super().releaseMouse()
        for w in self.windows.values():
            w.releaseMouse()

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        for w in self.windows.values():
            w.mouseReleaseEvent(event)

    def mousePressUpdate(self, event):
        super().mousePressUpdate(event)

        for window in self.windows.values():
            window.mousePressUpdate(event)

    def mousePressEvent(self, event):
        self.mousePressUpdate(event)

        mousePos = event.globalPos()
        x = mousePos.x()
        y = mousePos.y()

        for w in self.windows.values():
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

    def updateChildTracker(self, id):
        child = self.child(id)
        self.geometryTracker.updateGeometry(id, child.geometry())

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

    def resizeFromChild(self):
        if self.moving:
            return

        oldRect = self.geometry()
        newRect = self.geometryTracker.boundingBox()
        if newRect == QRect():
            newRect = self.defaultSize

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

    def isChild(self):
        return len(self.windows) == 0

    def child(self, id):
        return self.windows[id]
