from typing import cast

from PyQt5.QtCore import (
    QAbstractItemModel,
    QModelIndex,
    QSignalBlocker,
    QSize,
    Qt,
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

NOOP = ""
LOGICALS = ["AND", "OR", "NOT"]
COMPARISONS = ["<", ">", "==", "<=", ">=", "!="]

OPERATOR = "OPERATOR"
VALUE = "VALUE"
FUNC = "FUNC"

OPERATORS = [NOOP] + LOGICALS + COMPARISONS + ["FUNC"]

OPTIONS = OPERATORS + [VALUE]

logicalHints = {key: "(c1, c2, ...)" for key in LOGICALS}
comparatorHints = {key: "(v1, v2)" for key in COMPARISONS}
funcHint = {FUNC: "(func, v1, v2, ...)"}

TYPEHINTS = {}
TYPEHINTS.update(logicalHints)
TYPEHINTS.update(comparatorHints)
TYPEHINTS.update(funcHint)


def applyTypeHint(op):
    hint = TYPEHINTS.get(op)
    if not hint:
        return op

    return f"{op}  {hint}"


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

    def closeEvent(self, event):
        QApplication.quit()


class ExprEditor(QWidget):
    valueChanged = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.combo = QComboBox(self)
        self.combo.addItems(OPTIONS)
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

    def onOperatorChanged(self, text):
        self.line.setVisible(text == VALUE)
        self.addBtn.setVisible(text != VALUE)
        self.subBtn.setVisible(text != VALUE)


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

        editor.addBtn.clicked.connect(lambda: model.addChildValue(item))
        editor.subBtn.clicked.connect(lambda: model.removeChild(item))

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


class CustomItemModel(QStandardItemModel):
    def __init__(self):
        super().__init__()

    def data(self, index, role):
        if role == Qt.DisplayRole:
            editType = super().data(index, Qt.UserRole)
            value = super().data(index, Qt.EditRole)
            if editType == NOOP:
                return "Choose Option"

            elif editType == VALUE:
                return value if value else "Set Value"

            return applyTypeHint(editType)

        return super().data(index, role)

    def addChildValue(self, item):
        child = QStandardItem()
        child.setData(VALUE, Qt.UserRole)
        item.appendRow(child)

    def removeChild(self, item):
        if item.rowCount():
            item.removeRow(item.rowCount() - 1)


class App(QApplication):
    def __init__(self):
        super().__init__([])
        self.window = MainWindow()
        self.widget = QWidget()
        self.layout = QVBoxLayout(self.widget)

        self.widget.setLayout(self.layout)
        self.window.setCentralWidget(self.widget)
        self.window.show()

        model = QStandardItemModel(5, 5)
        for i in range(model.columnCount()):
            for j in range(model.rowCount()):
                model.setItem(i, j, QStandardItem(f"row {j}, column {i}"))

        table = QTableView()
        table.setModel(model)

        self.layout.addWidget(table)

        model = CustomItemModel()
        parent = model.invisibleRootItem()
        item = QStandardItem()
        item.setData(NOOP, Qt.UserRole)
        parent.appendRow(item)

        delegate = CustomItemDelegate()

        tree = QTreeView()
        tree.setItemDelegate(delegate)
        tree.setModel(model)
        self.layout.addWidget(tree)


app = App()
app.exec()
