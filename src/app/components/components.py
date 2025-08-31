from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QHeaderView, QTreeWidget, QTreeWidgetItem


class TreeWidgetCKLK(QTreeWidget):
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
