from PyQt5.QtCore import QAbstractTableModel, QModelIndex, Qt
from PyQt5.QtGui import QIcon, QImage, QPixmap

from src.app.components.runtime.model import RuntimeModel, RuntimeType


def array_to_icon(arr):
    h, w, c = arr.shape
    qimg = QImage(arr.data, w, h, w * c, QImage.Format_RGB888).copy()
    return QIcon(QPixmap.fromImage(qimg))


class RuntimeTableModel(QAbstractTableModel):
    def __init__(self, model: RuntimeModel, parent=None):
        super().__init__(parent)

        self.model = model
        self.keys = list(model.variables)

        model.itemCreated.connect(self.onItemCreated)
        model.itemDeleted.connect(self.onItemDeleted)
        model.itemUpdated.connect(self.onItemUpdated)
        model.modelCleared.connect(self.onModelCleared)
        model.modelLoaded.connect(self.onModelLoaded)

    def onItemCreated(self, key):
        row = len(self.keys)
        self.beginInsertRows(QModelIndex(), row, row)
        self.keys.append(key)
        self.endInsertRows()

    def onItemUpdated(self, key):
        row = self.keys.index(key)
        top = self.index(row, 0)
        bottom = self.index(row, self.columnCount(None) - 1)
        self.dataChanged.emit(top, bottom)

    def onItemDeleted(self, key):
        row = self.keys.index(key)
        self.beginRemoveRows(QModelIndex(), row, row)
        self.keys.pop(row)
        self.endRemoveRows()

    def onModelCleared(self):
        self.beginResetModel()
        self.keys.clear()
        self.endResetModel()

    def onModelLoaded(self):
        self.beginResetModel()
        self.keys = list(self.model.variables)
        self.endResetModel()

    def rowCount(self, parent: QModelIndex):
        return len(self.keys)

    def columnCount(self, parent: QModelIndex):
        return 3

    def data(self, index: QModelIndex, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None

        row = index.row()
        col = index.column()

        key = self.keys[row]
        item = self.model.getItem(key)

        if role == Qt.ItemDataRole.DisplayRole:
            match col:
                case 0:
                    return key
                case 1:
                    return item.type.name
                case 2:
                    if item.type == RuntimeType.IMAGE:
                        return (
                            f"{item.value.shape[1]}×{item.value.shape[0]}"
                            if item.value is not None
                            else ""
                        )
                    return str(item.value)

        if role == Qt.ItemDataRole.DecorationRole:
            if col == 2 and item.type == RuntimeType.IMAGE and item.value is not None:
                return array_to_icon(item.value)

        if role == Qt.ItemDataRole.UserRole:
            return item

        return None

    def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
        if role != Qt.EditRole:
            return False

        row = index.row()
        col = index.column()

        key = self.keys[row]
        if col == 2:
            patch = {"value": value}
            self.model.updateItem(key, patch)

            return True

        return False

    def flags(self, index):
        flags = super().flags(index)
        if not index.isValid():
            return flags

        if index.column() == 2:
            flags |= Qt.ItemIsEditable

        return flags

    def headerData(self, section, orientation, role):
        if role != Qt.ItemDataRole.DisplayRole:
            return None

        if orientation == Qt.Orientation.Horizontal:
            return ["Name", "Type", "Value"][section]

        return None
