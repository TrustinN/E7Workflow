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

from utils import (
    FUNC,
    LITERAL,
    NOOP,
    OPERATORS,
    VARIABLE,
    applyTypeHint,
    arity,
    parseLiteral,
)


@dataclass
class ExprNode:
    op: str = ""
    value: str = ""
    children: list["ExprNode"] = field(default_factory=list)
    parent: "ExprNode" = None

    def clearChildren(self):
        self.children.clear()

    def setOperator(self, op, value=None):
        self.op = op

        if op in (LITERAL, VARIABLE, FUNC) and value:
            self.value = value
        else:
            self.value = ""

    def addChild(self, node: "ExprNode"):
        node.parent = self
        self.children.append(node)

    def createChild(self):
        argc = arity(self.op)
        if argc is not None and len(self.children) >= argc:
            return False

        self.addChild(ExprNode())
        return True

    def popChild(self):
        if len(self.children) == 0:
            return False

        self.children.pop()
        return True

    def evaluate(self, context):
        context = context or {}
        if self.op == NOOP:
            return True
        if self.op == VARIABLE:
            return context[self.value]
        if self.op == LITERAL:
            return parseLiteral(self.value)
        if self.op == "AND":
            return all(c.evaluate(context) for c in self.children)
        if self.op == "OR":
            return any(c.evaluate(context) for c in self.children)
        if self.op == "NOT":
            return not self.children[0].evaluate(context)
        if self.op == "==":
            return self.children[0].evaluate(context) == self.children[1].evaluate(
                context
            )
        if self.op == "<":
            return self.children[0].evaluate(context) < self.children[1].evaluate(
                context
            )
        if self.op == ">":
            return self.children[0].evaluate(context) > self.children[1].evaluate(
                context
            )
        if self.op == "<=":
            return self.children[0].evaluate(context) <= self.children[1].evaluate(
                context
            )
        if self.op == ">=":
            return self.children[0].evaluate(context) >= self.children[1].evaluate(
                context
            )

        if self.op == "FUNC":
            func = context[self.value]
            args = [c.evaluate(context) for c in self.children]
            return func(*args)
        raise ValueError(f"Unknown op {self.op}")


class ExprModel(QAbstractItemModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.root: ExprNode = ExprNode()

    def setRoot(self, node: ExprNode):
        self.beginResetModel()
        self.root.clearChildren()
        self.root.addChild(node)
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
            if item.op in (LITERAL, VARIABLE):
                return item.value if item.value else "Set Value"

            if item.op == FUNC:
                decl = f" = {item.value}" if item.value else ""
                return f"{applyTypeHint(item.op)}{decl}"

            return applyTypeHint(item.op) if item.op else "Choose Option"

        if role == Qt.ItemDataRole.EditRole:
            return (item.op, item.value)

        return None

    def setData(self, index: QModelIndex, value: QVariant, role: Qt.ItemDataRole):
        item = self.itemFromIndex(index)
        op, val = value
        result = True

        if role == Qt.ItemDataRole.EditRole:
            item.setOperator(op, val)
            n = arity(item.op)
            if n is not None:
                while len(item.children) > n:
                    self.removeChildExpr(item)

                while len(item.children) < n:
                    self.addChildExpr(item)

        else:
            result = False

        if result:
            self.dataChanged.emit(index, index, [Qt.ItemDataRole.EditRole])

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
        success = item.createChild()
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
        self.line.setVisible(operator in (VARIABLE, LITERAL, FUNC))
        self.addBtn.setVisible(operator not in (VARIABLE, LITERAL))
        self.subBtn.setVisible(operator not in (VARIABLE, LITERAL))


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
        editType, data = index.data(Qt.EditRole)

        editor = cast(ExprEditor, editor)
        editor.setValue(editType, data)

    def setModelData(
        self, editor: QWidget, model: QAbstractItemModel, index: QModelIndex
    ):
        editor = cast(ExprEditor, editor)
        comboSelection, text = editor.value()
        model.setData(index, (comboSelection, text), Qt.EditRole)

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

        root = ExprNode("AND")

        model = ExprModel()
        model.setRoot(root)

        delegate = CustomItemDelegate()
        tree = ExprTreeView()
        tree.setItemDelegate(delegate)
        tree.setModel(model)
        self.layout.addWidget(tree)


app = App()
app.exec()
