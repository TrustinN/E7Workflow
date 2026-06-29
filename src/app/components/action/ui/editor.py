import json

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QStackedWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from .icon import ActionIconResolver


class ActionEditor(QWidget):
    actionChanged = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self.combo = QComboBox()
        self.combo.currentTextChanged.connect(self.setEditor)
        self.combo.currentTextChanged.connect(self.actionChanged.emit)
        self.layout.addWidget(self.combo)

        self.stack = QStackedWidget()
        self.layout.addWidget(self.stack)

        self.widgets = {}
        self.editors = {}
        self.actionSchemas = {}

    def addAction(self, info):
        name = info["name"]
        userParams = info["userParams"]
        result = info["result"]
        self.actionSchemas[name] = userParams

        self.combo.addItem(name)

        widget = self.createWidgetFromParams(name, userParams, result)

        self.widgets[name] = widget
        self.stack.addWidget(widget)

        if self.combo.count() == 1:
            self.combo.setCurrentText(name)

    def createWidgetFromParams(self, name, params, result):
        widget = QWidget()

        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)

        self.editors[name] = {}

        for key, param in params.items():
            row = QWidget()

            rowLayout = QHBoxLayout(row)
            rowLayout.setContentsMargins(0, 0, 0, 0)
            rowLayout.addWidget(QLabel(key))

            if param["type"] == "enum":
                editor = QComboBox()
                editor.addItems(param["values"])
                rowLayout.addWidget(editor)

                self.editors[name][key] = editor
                editor.currentTextChanged.connect(self.actionChanged.emit)

            elif param["type"] == "str":
                value = param.get("value")
                editor = QLineEdit()
                editor.setText(value)
                rowLayout.addWidget(editor)

                self.editors[name][key] = editor
                editor.textChanged.connect(self.actionChanged.emit)

            layout.addWidget(row)

        view = QTextEdit()
        view.setReadOnly(True)
        view.setPlainText(json.dumps(result, indent=2, ensure_ascii=False))
        layout.addWidget(view)
        layout.addStretch()

        return widget

    def getActionData(self):
        name = self.combo.currentText()
        schema = {}

        for key, param in self.actionSchemas[name].items():
            schema[key] = param.copy()
            editor = self.editors[name][key]
            if param["type"] == "enum":
                schema[key]["value"] = editor.currentText()
            elif param["type"] == "str":
                schema[key]["value"] = editor.text()

        return {
            "name": name,
            "userParams": schema,
            "icon": ActionIconResolver.resolveIcon(name, schema),
        }

    def setEditor(self, name):
        widget = self.widgets.get(name)

        if widget is not None:
            self.stack.setCurrentWidget(widget)
