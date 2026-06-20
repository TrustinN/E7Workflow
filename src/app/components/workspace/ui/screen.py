from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QPushButton, QShortcut, QVBoxLayout, QWidget


class WorkspaceScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)

        self.shortcut = QShortcut(QKeySequence.New, self)
        self.shortcut.setContext(Qt.ApplicationShortcut)
        key = self.shortcut.key().toString(QKeySequence.NativeText)
        self.btn = QPushButton(f"Add Workspace ({key})")
        self.layout.addWidget(self.btn)
        self.layout.addStretch()
