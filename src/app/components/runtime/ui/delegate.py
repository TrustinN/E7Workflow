from typing import cast

from PyQt5.QtCore import QModelIndex, Qt
from PyQt5.QtWidgets import QDoubleSpinBox, QLineEdit, QStyledItemDelegate, QWidget

from src.app.components.runtime.model import RuntimeType


class RuntimeDelegate(QStyledItemDelegate):

    def __init__(self, parent=None):
        super().__init__(parent)

    def createEditor(self, parent, option, index):
        item = index.data(Qt.ItemDataRole.UserRole)

        match item.type:
            case RuntimeType.NUM:
                editor = QDoubleSpinBox(parent)
                editor.setRange(-1e12, 1e12)
                editor.setDecimals(6)
                return editor

            case RuntimeType.STR:
                return QLineEdit(parent)

            case RuntimeType.IMAGE:
                return None

    def setEditorData(self, editor: QWidget, index: QModelIndex):
        item = index.data(Qt.ItemDataRole.UserRole)

        match item.type:
            case RuntimeType.NUM:
                editor = cast(QDoubleSpinBox, editor)
                if isinstance(item.value, (int, float)):
                    editor.setValue(item.value)

                else:
                    editor.setValue(0.0)

            case RuntimeType.STR:
                editor = cast(QLineEdit, editor)
                editor.setText(str(item.value))

            case RuntimeType.IMAGE:
                return None

    def setModelData(self, editor, model, index):
        item = index.data(Qt.ItemDataRole.UserRole)

        match item.type:
            case RuntimeType.NUM:
                editor = cast(QDoubleSpinBox, editor)
                model.setData(index, editor.value(), Qt.ItemDataRole.EditRole)

            case RuntimeType.STR:
                editor = cast(QLineEdit, editor)
                model.setData(index, editor.text(), Qt.ItemDataRole.EditRole)

            case RuntimeType.IMAGE:
                return
