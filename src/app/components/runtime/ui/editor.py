from PyQt5.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from src.app.components.runtime.model import RuntimeModel, RuntimeSchema, RuntimeType

from .delegate import RuntimeDelegate
from .model import RuntimeTableModel
from .view import RuntimeTable


class RuntimeEditor(QWidget):
    def __init__(self, model: RuntimeModel):
        super().__init__()
        self.layout = QVBoxLayout(self)

        self.model = model
        self.tableModel = RuntimeTableModel(model)
        self.delegate = RuntimeDelegate()

        self.table = RuntimeTable(self.model, self.tableModel, self.delegate)

        controls = QHBoxLayout()

        self.line = QLineEdit()
        self.line.setPlaceholderText("Variable name")

        self.combo = QComboBox()
        for rt in RuntimeType:
            self.combo.addItem(rt.name, rt)

        self.addBtn = QPushButton("+")
        self.deleteBtn = QPushButton("−")

        self.addBtn.setFixedWidth(45)
        self.deleteBtn.setFixedWidth(45)

        self.addBtn.clicked.connect(self.handleVariableAdd)
        self.deleteBtn.clicked.connect(self.handleVariableDelete)

        controls.addWidget(self.line, 1)
        controls.addWidget(self.combo)
        controls.addWidget(self.addBtn)
        controls.addWidget(self.deleteBtn)
        controls.setSpacing(2)

        self.layout.addWidget(self.table)
        self.layout.addLayout(controls)
        self.setMinimumWidth(300)

    def uniqueVariableName(self, name="var"):
        keys = set(self.model.getKeys())

        if name not in keys:
            return name

        i = 2
        while f"{name}{i}" in keys:
            i += 1

        return f"{name}{i}"

    def handleVariableAdd(self):
        runtimeType = self.combo.currentData()
        name = self.line.text()

        if not name:
            name = self.uniqueVariableName()

        self.model.addItem(name, RuntimeSchema(name=name, type=runtimeType))

    def handleVariableDelete(self):
        indexes = self.table.selectionModel().selectedRows()

        if not indexes:
            return

        row = indexes[0].row()
        key = self.tableModel.keys[row]
        self.model.deleteItem(key)
