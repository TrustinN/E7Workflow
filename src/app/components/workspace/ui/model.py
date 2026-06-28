from PyQt5.QtCore import QAbstractItemModel, QModelIndex, Qt

from src.app.components.workspace.model import WorkspaceModel, WorkspaceSchema


class WorkspaceItemModel(QAbstractItemModel):
    def __init__(self, model: WorkspaceModel, parent=None):
        super().__init__(parent)
        self.model = model
        self.model.modelCreated.connect(self.onCreated)
        self.model.modelUpdated.connect(self.onUpdated)
        self.model.modelDeleted.connect(self.onDeleted)
        self.model.modelCleared.connect(self.onClear)
        self.model.modelLoaded.connect(self.onLoad)

    def onCreated(self, id: str):
        item = self.model.getItem(id)
        parentItem = self.model.getItem(item.parent) if item.parent else None

        row = 0
        if parentItem is None:
            parentIndex = QModelIndex()

        else:
            parentIndex = self.indexFromItem(parentItem)
            row = parentItem.children.index(id)

        self.beginInsertRows(parentIndex, row, row)
        self.endInsertRows()

    def onUpdated(self, id: str):
        item = self.model.getItem(id)
        index = self.indexFromItem(item)
        if not index.isValid():
            return

        self.dataChanged.emit(index, index, [Qt.DisplayRole])

    def onDeleted(self, id: str):
        item = self.model.getItem(id)
        parentItem = self.model.getItem(item.parent) if item.parent else None

        row = 0
        if parentItem is None:
            parentIndex = QModelIndex()

        else:
            parentIndex = self.indexFromItem(parentItem)
            row = parentItem.children.index(item.id)

        self.beginRemoveRows(parentIndex, row, row)
        self.endRemoveRows()

    def onClear(self):
        self.beginResetModel()
        self.endResetModel()

    def onLoad(self):
        self.beginResetModel()
        self.endResetModel()

    def root(self):
        rootID = self.model.rootIndex()
        if not rootID:
            return None

        return self.model.getItem(rootID)

    def parent(self, index: QModelIndex):
        if not index.isValid():
            return QModelIndex()

        child = self.itemFromIndex(index)
        if not child.parent:
            return QModelIndex()

        parentItem = self.model.getItem(child.parent)
        return self.indexFromItem(parentItem)

    def index(self, row: int, col: int, parent: QModelIndex):
        parentItem = self.itemFromIndex(parent)
        if parentItem is None:
            return QModelIndex()

        childID = parentItem.children[row]
        child = self.model.getItem(childID)

        return self.createIndex(row, col, child)

    def itemFromIndex(self, index: QModelIndex) -> WorkspaceSchema:
        if index.isValid():
            return index.internalPointer()

        root = self.root()
        return root

    def indexFromItem(self, item: WorkspaceSchema):
        if item is self.root():
            return QModelIndex()

        row = self.model.getItem(item.parent).children.index(item.id)
        return self.createIndex(row, 0, item)

    def rowCount(self, parent: QModelIndex):
        if parent.isValid() and parent.column() > 0:
            return 0

        parentItem = self.itemFromIndex(parent)
        if parentItem is None:
            return 0

        return len(parentItem.children)

    def columnCount(self, parent: QModelIndex):
        return 3

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None

        item = self.itemFromIndex(index)
        col = index.column()
        if role in (Qt.DisplayRole, Qt.EditRole):
            if col == 0:
                return item.name

        if role == Qt.CheckStateRole:
            if col == 1:
                return Qt.Checked if item.visible else Qt.Unchecked

            if col == 2:
                return Qt.Checked if item.locked else Qt.Unchecked

        return None

    def setData(self, index, value, role=Qt.EditRole):
        if not index.isValid():
            return False

        item = self.itemFromIndex(index)
        col = index.column()

        if role == Qt.EditRole and col == 0:
            self.model.updateItem(item.id, {"name": str(value)})
            self.dataChanged.emit(index, index)
            return True

        if role == Qt.CheckStateRole:
            checked = value == Qt.Checked

            if col == 1:
                self.updateSubtree(item, "visible", checked)
                return True

            if col == 2:
                self.updateSubtree(item, "locked", checked)
                return True

        return False

    def headerData(self, section, orientation, role):
        if role != Qt.DisplayRole:
            return None

        if orientation == Qt.Horizontal:
            return ["Name", "Visible", "Locked"][section]

        return None

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled

        base = Qt.ItemIsEnabled | Qt.ItemIsSelectable
        if index.column() == 0:
            return base | Qt.ItemIsEditable

        if index.column() in (1, 2):
            return base | Qt.ItemIsUserCheckable

        return base

    def updateSubtree(self, item, key, value):
        items = self.collectSubtree(item)

        for node in items:
            self.model.updateItem(node.id, {key: value})

        for node in items:
            index = self.indexFromItem(node)
            self.dataChanged.emit(
                index.sibling(index.row(), 1),
                index.sibling(index.row(), 2),
                [Qt.CheckStateRole],
            )

    def collectSubtree(self, item):
        stack = [item]
        result = []

        while stack:
            node = stack.pop()
            result.append(node)

            for child_id in node.children:
                stack.append(self.model.getItem(child_id))

        return result
