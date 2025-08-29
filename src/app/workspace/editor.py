from nanoid import generate
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QInputDialog, QLineEdit, QPushButton, QVBoxLayout, QWidget

from .workspace import Workspace


class WorkspacEditorActions(QWidget):
    add_ = pyqtSignal()
    delete_ = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()

        self.buttonLabels = [
            "Add",
            "Delete",
        ]
        self.buttons = [QPushButton(label) for label in self.buttonLabels]
        self.signals = [
            self.add_,
            self.delete_,
        ]

        for btn, sig in zip(self.buttons, self.signals):
            self.layout.addWidget(btn)
            btn.clicked.connect(sig.emit)

        self.setLayout(self.layout)


class WorkspaceEditor(QWidget):
    def __init__(self):
        super().__init__()

    def addWorkspace(self, id=None, name=None):
        if not name:
            name, ok = QInputDialog.getText(
                self,
                "QInputDialog.getText()",
                "Workspace Name:",
                QLineEdit.Normal,
                "WS Name",
            )

        wks = None
        if id:
            wks = Workspace(id)
        else:
            wks = Workspace(generate())

        if name:
            wks.setName(name)

        wks.show()
        wks.unlock()

        return wks

    def deleteWorkspace(self):
        raise RuntimeError("Not Implemented")
