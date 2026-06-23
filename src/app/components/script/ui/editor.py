from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from .code import CodeEditor


class ScriptManager(QWidget):
    requestScript = pyqtSignal()
    requestSetScript = pyqtSignal()
    requestUnsetScript = pyqtSignal()
    editorUpdated = pyqtSignal(str)

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)
        note = QLabel(
            "Note: The script must define a function named "
            "'condition(context)'. The 'context' argument is a dictionary "
            "containing the current running state. The function should return "
            "True or False."
        )
        note.setWordWrap(True)

        layout.addWidget(note)

        self.codeTabs = QTabWidget()
        self.codeTabs.tabBarDoubleClicked.connect(self.renameTab)

        self.combo = QComboBox()

        addRow = QWidget()
        addLayout = QHBoxLayout(addRow)
        addLayout.setContentsMargins(0, 0, 0, 0)

        addButton = QPushButton("+")
        addButton.clicked.connect(self.requestScript.emit)

        addLayout.addWidget(QLabel("Add Script"))
        addLayout.addStretch()
        addLayout.addWidget(addButton)

        setRow = QWidget()
        setLayout = QHBoxLayout(setRow)
        setLayout.setContentsMargins(0, 0, 0, 0)

        setButton = QPushButton("Set")
        setButton.clicked.connect(self.requestSetScript.emit)

        setLayout.addWidget(QLabel("Set Script"))
        setLayout.addWidget(self.combo)
        setLayout.addWidget(setButton)

        unsetRow = QWidget()
        unsetLayout = QHBoxLayout(unsetRow)
        unsetLayout.setContentsMargins(0, 0, 0, 0)

        unsetButton = QPushButton("Unset")
        unsetButton.clicked.connect(self.requestUnsetScript.emit)

        unsetLayout.addWidget(QLabel("Unset Script"))
        unsetLayout.addWidget(unsetButton)

        layout.addWidget(self.codeTabs)
        layout.addWidget(addRow)
        layout.addWidget(setRow)
        layout.addWidget(unsetRow)

        self.editors = {}

    def addCodeTab(self, id, name):
        editor = CodeEditor()
        index = self.codeTabs.addTab(editor, name)
        self.codeTabs.setCurrentIndex(index)

        self.combo.addItem(name, userData=id)
        self.combo.setCurrentIndex(index)

        self.editors[id] = editor
        editor.textChanged.connect(lambda: self.editorUpdated.emit(id))

        return editor

    def currentEditor(self):
        editor = self.codeTabs.currentWidget()
        for key, val in self.editors.items():
            if editor == val:
                return key

    def setTabName(self, index, name):
        self.codeTabs.setTabText(index, name)
        self.combo.setItemText(index, name)
        id = self.combo.itemData(index)

        self.editorUpdated.emit(id)

    def renameTab(self, index):
        if index < 0:
            return

        oldName = self.codeTabs.tabText(index)
        newName, ok = QInputDialog.getText(
            self,
            "Rename Script",
            "Script name:",
            text=oldName,
        )

        if ok and newName.strip():
            self.setTabName(index, newName.strip())

    def getData(self, id):
        index = self.combo.findData(id)
        editor = self.editors[id]
        return {
            "id": id,
            "name": self.combo.itemText(index),
            "code": editor.text(),
        }

    def clearState(self):
        self.combo.clear()
        self.editors.clear()
        self.codeTabs.clear()

    def setData(self, id, data):
        name = data["name"]
        text = data["code"]

        self.addCodeTab(id, name)
        editor = self.editors[id]
        editor.setText(text)
