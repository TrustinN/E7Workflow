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
