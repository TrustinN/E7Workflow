from dataclasses import dataclass, field
from typing import Any, Optional, cast

from PyQt5.QtCore import (
    QAbstractItemModel,
    QModelIndex,
    QSignalBlocker,
    QSize,
    Qt,
    QVariant,
    pyqtSignal,
)
from PyQt5.QtGui import QStandardItem, QStandardItemModel
from PyQt5.QtWidgets import (
    QApplication,
    QComboBox,
    QHBoxLayout,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QStyledItemDelegate,
    QStyleOptionViewItem,
    QTableView,
    QTreeView,
    QVBoxLayout,
    QWidget,
)

from utils import FUNC, OPERATORS, VALUE, applyTypeHint, arity


@dataclass
class ExprNode:
    op: str = ""
    value: str = ""
    children: list["ExprNode"] = field(default_factory=list)
    parent: "ExprNode" = None

    def setOperator(self, op, value=""):
        self.op = op

        if op in (VALUE, FUNC):
            self.value = value
        else:
            self.value = ""

    def isValue(self):
        return self.op == VALUE

    def addChild(self):
        argc = arity(self.op)
        if argc is not None and len(self.children) >= argc:
            return False

        self.children.append(ExprNode(parent=self))
        return True

    def popChild(self):
        if len(self.children) == 0:
            return False

        self.children.pop()
        return True


class ExprModel(QAbstractItemModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.root: ExprNode = None

    def setRoot(self, root: ExprNode):
        self.beginResetModel()
        self.root = root
        self.endResetModel()

    def index(self, row: int, col: int, parent: QModelIndex):
        parentNode = self.itemFromIndex(parent)
        child = parentNode.children[row]

        return self.createIndex(row, col, child)

    def parent(self, index: QModelIndex):
        if not index.isValid():
            return QModelIndex()

        item = self.itemFromIndex(index)
        parentItem = item.parent
        return self.indexFromItem(parentItem)

    def rowCount(self, parent: QModelIndex):
        if parent.isValid() and parent.column() > 0:
            return 0

        item = self.itemFromIndex(parent)
        return len(item.children)

    def columnCount(self, parent: QModelIndex):
        return 1

    def data(self, index: QModelIndex, role=Qt.DisplayRole):
        if not index.isValid():
            return None

        item = self.itemFromIndex(index)

        if role == Qt.ItemDataRole.DisplayRole:
            if item.op == VALUE:
                return item.value if item.value else "Set Value"

            if item.op == FUNC:
                decl = f" = {item.value}" if item.value else ""
                return f"{applyTypeHint(item.op)}{decl}"

            return applyTypeHint(item.op) if item.op else "Choose Option"

        if role == Qt.ItemDataRole.EditRole:
            return item.value

        if role == Qt.ItemDataRole.UserRole:
            return item.op

        return None

    def setData(self, index: QModelIndex, value: QVariant, role: Qt.ItemDataRole):
        item = self.itemFromIndex(index)
        result = True

        if role == Qt.ItemDataRole.UserRole:
            item.setOperator(value)
            n = arity(item.op)
            if n is not None:
                while len(item.children) > n:
                    self.removeChildExpr(item)

                while len(item.children) < n:
                    self.addChildExpr(item)

        elif role == Qt.ItemDataRole.EditRole:
            op = index.data(Qt.ItemDataRole.UserRole)
            item.setOperator(op, value)

        else:
            result = False

        if result:
            self.dataChanged.emit(
                index, index, [Qt.ItemDataRole.UserRole, Qt.ItemDataRole.EditRole]
            )

        return result

    def itemFromIndex(self, index: QModelIndex) -> ExprNode:
        if index.isValid():
            return index.internalPointer()

        return self.root

    def indexFromItem(self, item: ExprNode):
        if item is self.root:
            return QModelIndex()

        row = item.parent.children.index(item)
        return self.createIndex(row, 0, item)

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags

        return Qt.ItemFlag.ItemIsEditable | QAbstractItemModel.flags(self, index)

    def addChildExpr(self, item: ExprNode):
        index = self.indexFromItem(item)
        row = len(item.children)

        self.beginInsertRows(index, row, row)
        success = item.addChild()
        self.endInsertRows()

        return success

    def removeChildExpr(self, item: ExprNode):
        index = self.indexFromItem(item)
        row = len(item.children) - 1

        self.beginRemoveRows(index, row, row)
        success = item.popChild()
        self.endRemoveRows()

        return success


class ExprTreeView(QTreeView):
    def setModel(self, model):
        super().setModel(model)
        model.rowsInserted.connect(self.onRowsInserted)

    def onRowsInserted(self, parent, first, last):
        self.expand(parent)


class ExprEditor(QWidget):
    valueChanged = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.combo = QComboBox(self)
        self.combo.addItems(list(OPERATORS.keys()))
        self.line = QLineEdit(self)
        self.line.setVisible(False)
        self.addBtn = QPushButton("+")
        self.subBtn = QPushButton("-")

        layout = QHBoxLayout(self)
        layout.addWidget(self.combo)
        layout.addWidget(self.line)
        layout.addWidget(self.addBtn)
        layout.addWidget(self.subBtn)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        h = max(
            self.combo.sizeHint().height(),
            self.line.sizeHint().height(),
            self.addBtn.sizeHint().height(),
            self.subBtn.sizeHint().height(),
        )

        self.combo.setFixedHeight(h)
        self.line.setFixedHeight(h)

        self.addBtn.setFixedSize(int(1.4 * h), h)
        self.subBtn.setFixedSize(int(1.4 * h), h)

        self.combo.currentTextChanged.connect(self.valueChanged.emit)
        self.combo.currentTextChanged.connect(self.onOperatorChanged)
        self.line.textChanged.connect(self.valueChanged.emit)

    def setValue(self, operator, value=None):
        with QSignalBlocker(self.combo), QSignalBlocker(self.line):
            self.combo.setCurrentText(operator)
            if value is not None:
                self.line.setText(value)
            else:
                self.line.clear()

            self.onOperatorChanged(operator)

    def value(self) -> tuple[str, str]:
        return (
            self.combo.currentText(),
            self.line.text(),
        )

    def onOperatorChanged(self, operator):
        self.line.setVisible(operator in (VALUE, FUNC))
        self.addBtn.setVisible(operator != VALUE)
        self.subBtn.setVisible(operator != VALUE)


class CustomItemDelegate(QStyledItemDelegate):
    def __init__(self):
        super().__init__()

    def createEditor(
        self, parent: QWidget, option: QStyleOptionViewItem, index: QModelIndex
    ):
        editor = ExprEditor(parent)
        editor.valueChanged.connect(lambda: self.commitData.emit(editor))

        model = index.model()
        item = model.itemFromIndex(index)

        editor.addBtn.clicked.connect(lambda: model.addChildExpr(item))
        editor.subBtn.clicked.connect(lambda: model.removeChildExpr(item))

        return editor

    def setEditorData(self, editor: QWidget, index: QModelIndex):
        editType = index.data(Qt.UserRole)
        data = index.data(Qt.EditRole)

        editor = cast(ExprEditor, editor)
        editor.setValue(editType, data)

    def setModelData(
        self, editor: QWidget, model: QAbstractItemModel, index: QModelIndex
    ):
        editor = cast(ExprEditor, editor)
        comboSelection, text = editor.value()
        model.setData(index, comboSelection, Qt.UserRole)
        model.setData(index, text, Qt.EditRole)

    def updateEditorGeometry(
        self, editor: QWidget, option: QStyleOptionViewItem, index: QModelIndex
    ):
        editor.setGeometry(option.rect)

    def paint(self, painter, option, index):
        view = option.widget
        if view.isPersistentEditorOpen(index):
            return

        super().paint(painter, option, index)

    def sizeHint(self, option, index):
        size = super().sizeHint(option, index)
        size.setHeight(28)
        return size


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

    def closeEvent(self, event):
        QApplication.quit()


class App(QApplication):
    def __init__(self):
        super().__init__([])
        self.window = MainWindow()
        self.widget = QWidget()
        self.layout = QVBoxLayout(self.widget)

        self.widget.setLayout(self.layout)
        self.window.setCentralWidget(self.widget)
        self.window.show()

        root = ExprNode("ROOT")
        andNode = ExprNode("AND", parent=root)
        root.children.append(andNode)

        model = ExprModel()
        model.setRoot(root)

        delegate = CustomItemDelegate()
        tree = ExprTreeView()
        tree.setItemDelegate(delegate)
        tree.setModel(model)
        self.layout.addWidget(tree)


def resolveValue(value: str, context: dict[str, Any]):
    return 0


def evaluate(node: ExprNode, context: dict[str, Any] = None):
    context = context or {}
    if node.op == "VALUE":
        return resolveValue(node.value, context)

    if node.op == "AND":
        return all(evaluate(c, context) for c in node.children)

    if node.op == "OR":
        return any(evaluate(c, context) for c in node.children)

    if node.op == "NOT":
        return not evaluate(node.children[0], context)

    if node.op == "==":
        return evaluate(node.children[0], context) == evaluate(
            node.children[1], context
        )

    if node.op == "<":
        return evaluate(node.children[0], context) < evaluate(node.children[1], context)

    raise ValueError(f"Unknown op {node.op}")


app = App()
app.exec()
