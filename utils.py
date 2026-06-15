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
LITERAL = "LITERAL"
VARIABLE = "VARIABLE"
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
    LITERAL: {
        "arity": 0,
        "hint": "",
    },
    VARIABLE: {
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


def parseLiteral(text: str):
    text = text.strip()

    if text.lower() == "true":
        return True

    if text.lower() == "false":
        return False

    if text.lower() == "":
        return None

    try:
        return int(text)
    except ValueError:
        pass

    try:
        return float(text)
    except ValueError:
        pass

    if len(text) >= 2 and text[0] == text[-1] and text[0] in ("'", '"'):
        return text[1:-1]

    raise ValueError(f"Not a literal: {text}")
