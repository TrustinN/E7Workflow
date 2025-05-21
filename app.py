import copy
import json
import os

import numpy as np
from PyQt5.QtCore import QObject, QPoint, QRect, Qt, pyqtSignal
from PyQt5.QtGui import QBrush, QColor, QPainter, QPen, QRegion
from PyQt5.QtWidgets import (
    QApplication,
    QCheckBox,
    QHBoxLayout,
    QHeaderView,
    QMainWindow,
    QPushButton,
    QSpinBox,
    QSplitter,
    QTabWidget,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

CONFIG_PATH = "config"


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

    def children(self):
        return self["children"]

    def config(self):
        return self["config"]


class SelectionWindow(QWidget):
    resizeSignal = pyqtSignal()
    moveSignal = pyqtSignal()

    def __init__(self, name):
        super().__init__()
        self.name = name

        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.color = QColor(255, 255, 255, 10)

        self.dragPosition = QPoint()
        self.resizeMode = False
        self.resizeIndices = None
        self.resizeError = (np.array([0.0, 0.0]), np.array([0.0, 0.0]))
        self.fixed = False

        self.show()

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

    def mousePressEvent(self, event):
        if self.canMove():
            self.grabMouse()

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

    def mouseReleaseEvent(self, event):
        self.releaseMouse()

    def resizeEvent(self, event):
        maskedRegion = QRegion(
            self.rect(),
            QRegion.RegionType.Rectangle,
        )
        self.setMask(maskedRegion)

    def setColor(self, color):
        self.color = color

    def getColor(self):
        return self.color

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        brush = QBrush(self.color)
        painter.setBrush(brush)

        rect = self.rect()
        painter.drawRect(rect.adjusted(2, 2, -2, -2))

        # Set text color and font for the title
        painter.setPen(QPen(QColor(255, 255, 255), 1))
        font = painter.font()
        font.setPointSize(12)
        font.setBold(True)
        painter.setFont(font)

        # Add padding to the top
        padding_top = 10  # Adjust padding as needed
        text_rect = rect.adjusted(0, padding_top, 0, 0)

        # Draw the title text
        painter.drawText(text_rect, Qt.AlignTop | Qt.AlignHCenter, self.name)

    def getBBox(self):
        return [
            self.frameGeometry().topLeft(),
            self.frameGeometry().bottomRight(),
        ]

    def lock(self):
        self.fixed = True

    def unlock(self):
        self.fixed = False

    def canMove(self):
        return not self.fixed


class Workspace(QObject):
    def __init__(self, name):
        super().__init__()
        self.name = name
        self.window = SelectionWindow(name)
        self.window.setWindowTitle(name)
        self.window.show()
        self.resizeSignal = self.window.resizeSignal
        self.moveSignal = self.window.moveSignal

    def disableSignals(self, slot):
        self.resizeSignal.disconnect(slot)
        self.moveSignal.disconnect(slot)

    def connectSignals(self, slot):
        self.resizeSignal.connect(slot)
        self.moveSignal.connect(slot)

    def hide(self):
        self.window.hide()

    def show(self):
        self.window.show()

    def lock(self):
        self.window.lock()

    def unlock(self):
        self.window.unlock()

    def canMove(self):
        return self.window.canMove()

    def getBBox(self):
        return self.window.getBBox()

    def setGeometry(self, rect):
        self.window.setGeometry(rect)
        self.resizeSignal.emit()

    def mousePressEvent(self, event):
        self.window.mousePressEvent(event)

    def mouseMoveEvent(self, event):
        self.window.mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.window.mouseReleaseEvent(event)

    def exportData(self, extract):
        return extract(self)

    def importData(self, apply, data):
        apply(self, data.config())


class WorkspaceLayout(Workspace):

    def __init__(self, name, wkspaces):
        super().__init__(name)
        self.padding = 15
        self.wkspaces = wkspaces
        for wkspace in self.wkspaces:
            wkspace.connectSignals(self.updateGeometry)
        self.updateGeometry()

        self.oldMouseMoveEvent = self.window.mouseMoveEvent
        self.oldMousePressEvent = self.window.mousePressEvent
        self.oldMouseReleaseEvent = self.window.mouseReleaseEvent

        self.window.mouseMoveEvent = self.mouseMoveEvent
        self.window.mousePressEvent = self.mousePressEvent
        self.window.mouseReleaseEvent = self.mouseReleaseEvent

        self.childFocused = None

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
        def wksResize(wks):
            oldTl, oldBr = wks.getBBox()

            # linear interpolation
            s0 = (1.0 * oldTl.x() - oldCornersPadded[0].x()) / dimOld.x()
            t0 = (1.0 * oldTl.y() - oldCornersPadded[0].y()) / dimOld.y()
            s1 = (1.0 * oldBr.x() - oldCornersPadded[1].x()) / dimOld.x()
            t1 = (1.0 * oldBr.y() - oldCornersPadded[1].y()) / dimOld.y()

            prevTlErr, prevBrErr = wks.window.resizeError
            newTlx = dimNew.x() * s0 + newCornersPadded[0].x() + prevTlErr[0]
            newTly = dimNew.y() * t0 + newCornersPadded[0].y() + prevTlErr[1]
            newBrx = dimNew.x() * s1 + newCornersPadded[1].x() + prevBrErr[0]
            newBry = dimNew.y() * t1 + newCornersPadded[1].y() + prevBrErr[1]

            newTl = np.array([newTlx, newTly])
            newBr = np.array([newBrx, newBry])

            intNewTl = newTl.astype(int)
            intNewBr = newBr.astype(int)

            wks.window.resizeError = (newTl - intNewTl, newBr - intNewBr)

            newTl = QPoint(intNewTl[0], intNewTl[1])
            newBr = QPoint(intNewBr[0], intNewBr[1])

            wks.setGeometry(QRect(newTl, newBr))

        def recursiveResize(wkspace):
            wksResize(wkspace)
            if hasattr(wkspace, "wkspaces"):
                for wks in wkspace.wkspaces:
                    recursiveResize(wks)

        for wks in self.wkspaces:
            recursiveResize(wks)

        self.window.setGeometry(QRect(newCorners[0], newCorners[1]))

    def mouseMoveEvent(self, event):
        if self.childFocused is not None:
            self.window.releaseMouse()
            self.childFocused.window.grabMouse()
        else:
            if not self.canMove():
                return

            if self.window.resizeMode:
                newCorners = self.getBBox()

                # Compute displacement
                for i in self.window.resizeIndices:
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

                self.oldMouseMoveEvent(event)
                for wkspace in self.wkspaces:
                    wkspace.window.mouseMoveEvent(event)

                # Recover children state
                for i in range(len(self.wkspaces)):
                    # Reenable signals
                    w.connectSignals(self.updateGeometry)
                    w = self.wkspaces[i]
                    if not unlockState[i]:
                        w.lock()

    def mousePressEvent(self, event):

        self.oldMousePressEvent(event)
        self.window.releaseMouse()
        mousePos = event.globalPos()
        x = mousePos.x()
        y = mousePos.y()

        for wkspace in self.wkspaces:
            wkspace.mousePressEvent(event)
            wkspace.mouseReleaseEvent(event)

        if self.childFocused:
            self.childFocused.window.mouseReleaseEvent(event)
            self.childFocused = None

        for w in self.wkspaces:
            tl, br = w.getBBox()
            if not w.canMove():
                continue

            # Find child under mouse press
            if tl.x() < x and x < br.x():
                if tl.y() < y and y < br.y():
                    self.childFocused = w
                    self.childFocused.window.setFocus()
                    self.childFocused.window.raise_()
                    self.childFocused.window.activateWindow()
                    self.childFocused.window.mousePressEvent(event)
                    return

        if self.canMove():
            self.window.setFocus()
            self.window.grabMouse()

    def mouseReleaseEvent(self, event):
        if self.childFocused:
            self.childFocused.window.mouseReleaseEvent(event)
            self.childFocused = None
        self.window.releaseMouse()

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

            self.window.setGeometry(QRect(tl, br))
        self.resizeSignal.emit()

    def setGeometry(self, rect):
        newTl, newBr = rect.topLeft(), rect.bottomRight()
        self.resize([newTl, newBr])
        self.resizeSignal.emit()

    def hide(self):
        self.window.hide()
        for wkspace in self.wkspaces:
            wkspace.hide()

    def show(self):
        self.window.show()
        for wkspace in self.wkspaces:
            wkspace.show()

    def lock(self):
        self.window.lock()
        for wkspace in self.wkspaces:
            wkspace.lock()

    def unlock(self):
        self.window.unlock()
        for wkspace in self.wkspaces:
            wkspace.unlock()

    def canMove(self):
        return self.window.canMove()

    def exportData(self, extract):
        data = extract(self)
        config = ConfigurationHierarchy(data)
        for wks in self.wkspaces:
            config.addChildConfig(wks.name, wks.exportData(extract))
        return config

    def importData(self, apply, data):
        apply(self, data.config())
        childData = data.children()
        for wks in self.wkspaces:
            if wks.name not in childData:
                continue
            subData = childData[wks.name]
            wks.importData(apply, subData)


class GlobalState(dict):
    def __init__(self):
        super().__init__()
        self["userState"] = {}

    def addWorkflowState(self, wkflow: "Workflow"):
        self[wkflow.name] = WorkflowState()

    def getWorkflowState(self, name: str) -> "WorkflowState":
        return self[name]

    def getUserState(self):
        return self["userState"]


class WorkflowState(dict):
    def __init__(self):
        super().__init__()
        self["temp"] = {}
        self["stats"] = {}

    def getTemporaryState(self):
        return self["temp"]

    def getWorkflowStats(self):
        return self["stats"]


class Chainable:

    def __init__(self):
        self.next = None

    def execute(self, state):
        pass

    def chain(self, chainable):
        newChainable = copy.deepcopy(self)
        prevExecute = newChainable.execute

        def chainExecute(state):
            prevExecute(state)
            chainable.execute(state)

        newChainable.execute = chainExecute
        return newChainable


class Task(Chainable):
    def __init__(self):
        self.kwargs = None
        self.wkspace = None

    def execute(self, state):
        assert self.func is not None
        assert self.kwargs is not None
        assert self.wkspace is not None

        self.func(self.wkspace, state, **self.kwargs)

    def setFunc(self, func, **kwargs):
        self.func = func
        self.kwargs = kwargs

    def setWorkspace(self, wkspace):
        self.wkspace = wkspace


class Workflow:
    def __init__(self, name, exec, wkspaces):
        self.name = name
        self.exec = exec
        self.wkspaces = wkspaces
        self.wkspaceLayout = WorkspaceLayout(name, self.wkspaces)
        self.window = self.wkspaceLayout.window

    def disableSignals(self, slot):
        self.window.resizeSignal.disconnect(slot)
        self.window.moveSignal.disconnect(slot)

    def connectSignals(self, slot):
        self.window.resizeSignal.connect(slot)
        self.window.moveSignal.connect(slot)

    def hide(self):
        self.wkspaceLayout.hide()

    def show(self):
        self.wkspaceLayout.show()

    def lock(self):
        self.wkspaceLayout.lock()

    def unlock(self):
        self.wkspaceLayout.unlock()

    def canMove(self):
        return self.window.canMove()

    def getBBox(self):
        return self.wkspaceLayout.getBBox()

    def setGeometry(self, rect):
        self.window.setGeometry(rect)
        self.window.resizeSignal.emit()

    def mousePressEvent(self, event):
        self.window.mousePressEvent(event)

    def mouseMoveEvent(self, event):
        self.window.mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.window.mouseReleaseEvent(event)

    def execute(self, state: GlobalState):
        self.exec(state)

    def exportData(self, extract):
        return self.wkspaceLayout.exportData(extract)

    def importData(self, apply, config):
        if config:
            self.wkspaceLayout.importData(apply, config)


def exportData(wkflow, dest, extract):
    data = wkflow.exportData(extract)
    configPath = os.path.join(CONFIG_PATH, f"{dest}.json")
    with open(configPath, "w") as file:
        json.dump(data, file)


def importData(src):
    configPath = os.path.join(CONFIG_PATH, f"{src}.json")
    if not os.path.exists(configPath):
        print("Config file does not exist")
        return None

    with open(configPath, "r") as file:
        data = json.load(file)
        config = ConfigurationHierarchy()
        config.setData(data)
        QApplication.processEvents()
        return config


def applyGeometry(wks, config):
    wks.window.setGeometry(layoutToBBox(config))
    QApplication.processEvents()


def extractGeometry(wks):
    return bboxToLayout(wks.window.getBBox())


def applyColor(wks, config):
    wks.window.setColor(listToColor(config))


def extractColor(wks):
    return colorToList(wks.window.getColor())


def fmtLayoutFile(wks):
    return f"{wks.name} Layout"


def fmtColorFile(wks):
    return f"{wks.name} Color"


class WorkflowRunner(QObject):
    stepFinished = pyqtSignal(GlobalState, Workflow)
    executeFinish = pyqtSignal(GlobalState, Workflow)

    def __init__(self):
        super().__init__()
        self.iterations = 1
        self.state = GlobalState()

    def setIterations(self, iterations):
        self.iterations = iterations

    def bindWorkflow(self, wkflow):
        self.wkflow = wkflow

    def setState(self, state):
        self.state = state

    def updateState(self, state):
        self.state.update(state)

    def run(self):
        self.wkflow.hide()
        QApplication.processEvents()
        for i in range(self.iterations):
            self.wkflow.execute(self.state)
            self.stepFinished.emit(self.state, self.wkflow)
        self.wkflow.show()

        self.executeFinish.emit(self.state, self.wkflow)


class ConfirmButton(QWidget):
    confirmClicked = pyqtSignal()

    def __init__(self, name):
        super().__init__()
        self.layout = QHBoxLayout()
        self.checkbox = QCheckBox()
        self.btn = QPushButton(name)

        self.layout.addWidget(self.checkbox)
        self.layout.addWidget(self.btn)

        self.setLayout(self.layout)

        self.btn.clicked.connect(self.confirmClickedEmit)

    def confirmClickedEmit(self):
        if self.checkbox.isChecked():
            self.confirmClicked.emit()


class WorkspaceTreeWidget(QTreeWidget):
    checkUpdated = pyqtSignal(QTreeWidgetItem, object)
    lockUpdated = pyqtSignal(QTreeWidgetItem, object)

    def __init__(self, name):
        super().__init__()
        self.itemChanged.connect(self.onItemChanged)
        self.nextId = 0
        self.treeItemToEntryMap = {}
        self.setColumnCount(2)
        self.setHeaderLabels([name, "Locked"])
        header = self.header()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setStretchLastSection(False)

        self.columnCascadeUpdates = {
            0: self.cascadeCheckState,
            1: self.cascadeCheckState,
        }
        self.columnCascadeFinishSig = {
            0: self.checkUpdated,
            1: self.lockUpdated,
        }
        self.columnUpdateCnts = {0: 0, 1: 0}

    def onItemChanged(self, item, column):
        onFinish = self.columnCascadeFinishSig[column]
        cascadeUpdate = self.columnCascadeUpdates[column]

        self.columnUpdateCnts[column] += 1
        cascadeUpdate(item)
        self.columnUpdateCnts[column] -= 1
        if self.columnUpdateCnts[column] == 0:
            onFinish.emit(item, column)

    def cascadeCheckState(self, item):
        checkState = item.checkState(0)
        for i in range(item.childCount()):
            child = item.child(i)
            childCheckState = child.checkState(0)
            if childCheckState != checkState:
                child.setCheckState(0, checkState)

    def addTreeItem(self, parent):
        widget = QTreeWidgetItem(parent)
        widget.setCheckState(0, Qt.Checked)
        widget.setCheckState(1, Qt.Unchecked)
        self.setItemId(widget)
        return widget

    def setItemId(self, item):
        item.id = self.nextId
        self.nextId += 1

    def getEntry(self, treeItem):
        return self.treeItemToEntryMap[treeItem.id]

    def setEntry(self, treeItem, entry):
        self.treeItemToEntryMap[treeItem.id] = entry

    def isChecked(self, treeItem, column):
        return treeItem.checkState(column) == Qt.Checked


class WorkflowWindow(QWidget):
    def __init__(self, name):
        super().__init__()
        self.name = name

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.splitter = QSplitter()
        layout.addWidget(self.splitter)

        builtinWindow = QWidget()
        layout = QVBoxLayout()
        builtinWindow.setLayout(layout)
        self.customWindow = None
        self.splitter.addWidget(builtinWindow)

        self.saveLayoutBtn = ConfirmButton("Save Layout")
        layout.addWidget(self.saveLayoutBtn)
        self.saveLayoutBtn.confirmClicked.connect(
            lambda: exportData(self.wkflow, fmtLayoutFile(self), extractGeometry)
        )

        self.loadLayoutBtn = QPushButton("Load Layout")
        layout.addWidget(self.loadLayoutBtn)
        self.loadLayoutBtn.clicked.connect(
            lambda: self.wkflow.importData(
                applyGeometry, importData(fmtLayoutFile(self))
            )
        )

        self.treeLayout = WorkspaceTreeWidget(name)
        layout.addWidget(self.treeLayout)

        self.execCnt = QSpinBox()
        self.execCnt.setValue(1)
        layout.addWidget(self.execCnt)

        # Add pane locking, colored panes
        self.execBtn = QPushButton("Execute")
        layout.addWidget(self.execBtn)

    def bindWorkflow(self, wkflow):
        self.wkflow = wkflow

        def recursiveAdd(parent, wks):
            widget = self.treeLayout.addTreeItem(parent)
            widget.setText(0, wks.name)
            self.treeLayout.setEntry(widget, wks)
            if hasattr(wks, "wkspaces"):
                for childWks in wks.wkspaces:
                    recursiveAdd(widget, childWks)

            return widget

        recursiveAdd(self.treeLayout, wkflow)
        self.treeLayout.checkUpdated.connect(self.updateWorkspaceVisibility)
        self.treeLayout.lockUpdated.connect(self.updateWorkspaceMutability)

    def updateWorkspaceVisibility(self, item, column):
        checked = self.treeLayout.isChecked(item, column)
        wks = self.treeLayout.getEntry(item)
        if checked:
            wks.show()
        else:
            wks.hide()

    def updateWorkspaceMutability(self, item, column):
        locked = self.treeLayout.isChecked(item, column)
        wks = self.treeLayout.getEntry(item)
        if locked:
            wks.lock()
        else:
            wks.unlock()

    def addWidget(self, widget):
        if self.customWindow is None:
            self.customWindow = QWidget()
            self.customLayout = QVBoxLayout()
            self.customWindow.setLayout(self.customLayout)
            self.splitter.addWidget(self.customWindow)
            self.customWindow.show()

        self.customLayout.addWidget(widget)

    def getLayout(self):
        return self.customLayout

    def getWindow(self):
        return self.customWindow


class E7WorkflowApp(QApplication):
    def __init__(self):
        super().__init__([])
        self.windows = {}
        self.wkflows = {}
        self.runners = {}

        self.mainWindow = QMainWindow()
        self.tabWidget = QTabWidget()
        self.tabWidget.currentChanged.connect(self.onTabChanged)
        self.mainWindow.setCentralWidget(self.tabWidget)
        self.mainWindow.show()

    def addWorkflow(self, wkflow, initialState=None):
        if self.tabWidget.count() == 0:
            wkflow.show()
        else:
            wkflow.hide()

        win = WorkflowWindow(wkflow.name)

        runner = WorkflowRunner()
        win.execCnt.valueChanged.connect(runner.setIterations)
        win.execBtn.clicked.connect(runner.run)

        self.windows[wkflow.name] = win
        self.wkflows[wkflow.name] = wkflow
        self.runners[wkflow.name] = runner

        runner.bindWorkflow(wkflow)
        if initialState:
            runner.updateState(initialState)

        win.bindWorkflow(wkflow)

        wkflowLayout = importData(f"{wkflow.name} Layout")
        wkflow.importData(applyGeometry, wkflowLayout)

        self.tabWidget.addTab(win, wkflow.name)

    def getWindow(self, name) -> WorkflowWindow:
        return self.windows[name]

    def getRunner(self, name) -> WorkflowRunner:
        return self.runners[name]

    def getWorkflow(self, name) -> Workflow:
        return self.wkflows[name]

    def onTabChanged(self, index):
        activeTitle = self.tabWidget.tabText(index)
        for w in self.wkflows:
            wf = self.wkflows[w]
            if w != activeTitle:
                wf.hide()
            else:
                wf.show()
