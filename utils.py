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
VALUE = "VALUE"
FUNC = "FUNC"

OPERATORS = {
    NOOP: {
        "arity": 0,
        "hint": "",
    },
    "AND": {
        "arity": None,
        "hint": "(c1, c2, ...)",
    },
    "OR": {
        "arity": None,
        "hint": "(c1, c2, ...)",
    },
    "NOT": {
        "arity": 1,
        "hint": "(c1)",
    },
    "<": {
        "arity": 2,
        "hint": "(v1, v2)",
    },
    ">": {
        "arity": 2,
        "hint": "(v1, v2)",
    },
    "==": {
        "arity": 2,
        "hint": "(v1, v2)",
    },
    "<=": {
        "arity": 2,
        "hint": "(v1, v2)",
    },
    ">=": {
        "arity": 2,
        "hint": "(v1, v2)",
    },
    "!=": {
        "arity": 2,
        "hint": "(v1, v2)",
    },
    FUNC: {
        "arity": None,
        "hint": "(func, v1, v2, ...)",
    },
    VALUE: {
        "arity": 0,
        "hint": "",
    },
}


def arity(op: str) -> int | None:
    return OPERATORS[op]["arity"]


def typeHint(op: str) -> str:
    return OPERATORS[op]["hint"]


def applyTypeHint(op: str) -> str:
    hint = typeHint(op)
    return f"{op} {hint}" if hint else op
