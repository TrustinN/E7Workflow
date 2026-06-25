from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QPushButton, QShortcut, QVBoxLayout, QWidget


class RunnerEditor(QWidget):
    requestActionSet = pyqtSignal()
    requestScriptSet = pyqtSignal()
    requestEntrySet = pyqtSignal()
    requestExecute = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout(self)

        self.actionShortcut = QShortcut("3", self)
        key = self.actionShortcut.key().toString(QKeySequence.NativeText)
        self.actionBtn = QPushButton(f"Set Action ({key})")
        self.actionShortcut.activated.connect(self.requestActionSet.emit)
        self.actionBtn.clicked.connect(self.requestActionSet.emit)
        self.actionShortcut.setContext(Qt.ApplicationShortcut)

        self.scriptShortcut = QShortcut("4", self)
        key = self.scriptShortcut.key().toString(QKeySequence.NativeText)
        self.scriptBtn = QPushButton(f"Set Script ({key})")
        self.scriptShortcut.activated.connect(self.requestScriptSet.emit)
        self.scriptBtn.clicked.connect(self.requestScriptSet.emit)
        self.scriptShortcut.setContext(Qt.ApplicationShortcut)

        self.entryShortcut = QShortcut("Return", self)
        key = self.entryShortcut.key().toString(QKeySequence.NativeText)
        self.entryBtn = QPushButton(f"Set Entry ({key})")
        self.entryShortcut.activated.connect(self.requestEntrySet)
        self.entryBtn.clicked.connect(self.requestEntrySet)
        self.entryShortcut.setContext(Qt.ApplicationShortcut)

        self.executeShortcut = QShortcut("Ctrl+R", self)
        key = self.executeShortcut.key().toString(QKeySequence.NativeText)
        self.executeBtn = QPushButton(f"Execute ({key})")
        self.executeShortcut.activated.connect(self.requestExecute)
        self.executeBtn.clicked.connect(self.requestExecute)
        self.executeShortcut.setContext(Qt.ApplicationShortcut)

        self.layout.addWidget(self.actionBtn)
        self.layout.addWidget(self.scriptBtn)
        self.layout.addWidget(self.entryBtn)
        self.layout.addWidget(self.executeBtn)
