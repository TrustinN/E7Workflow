from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)


class ActionEditor(QWidget):
    requestSetAction = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self.actionBtn = QPushButton("Set Action")
        self.actionBtn.clicked.connect(self.requestSetAction.emit)

        self.combo = QComboBox()
        self.combo.currentTextChanged.connect(self.actionChanged)
        self.layout.addWidget(self.actionBtn)
        self.layout.addWidget(self.combo)

        self.stack = QStackedWidget()
        self.layout.addWidget(self.stack)

        self.layout.addStretch()

        self.widgets = {}
        self.editors = {}
        self.actionSchemas = {}

    def addAction(self, info):
        name = info["name"]
        userParams = info["userParams"]
        self.actionSchemas[name] = userParams

        self.combo.addItem(name)

        widget = self.createWidgetFromParams(name, userParams)

        self.widgets[name] = widget
        self.stack.addWidget(widget)

        if self.combo.count() == 1:
            self.combo.setCurrentText(name)

    def createWidgetFromParams(self, name, params):
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

            layout.addWidget(row)

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

        return {"name": name, "userParams": schema}

    def actionChanged(self, name):
        widget = self.widgets.get(name)

        if widget is not None:
            self.stack.setCurrentWidget(widget)
