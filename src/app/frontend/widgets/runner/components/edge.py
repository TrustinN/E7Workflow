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


class EdgeEditorList(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout(self)
        self.editors: dict[str, EdgeEditorItem] = {}

    def addEdge(self, n1, n2):
        editor = EdgeEditorItem(n1, n2)
        self.editors[n2] = editor
        self.layout.addWidget(editor)

    def addItem(self, cond):
        for editor in self.editors.values():
            editor.addItem(cond)

    def getItem(self, index):
        editor = self.editors[index]
        return editor.getItem()


class EdgeEditorItem(QWidget):
    def __init__(self, n1, n2):
        super().__init__()

        self.layout = QHBoxLayout(self)
        self.layout.addWidget(QLabel(n1))
        self.layout.addWidget(QLabel("---->"))
        self.layout.addWidget(QLabel(n2))

        self.combo = QComboBox()
        self.layout.addWidget(self.combo)
        self.layout.addStretch()

    def addItem(self, cond):
        self.combo.addItem(cond)

    def getItem(self):
        return self.combo.currentText()


class EdgeEditor(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout(self)

        self.stack = QStackedWidget()
        self.layout.addWidget(self.stack)
        self.layout.addStretch()

        self.widgets: dict[str, EdgeEditorList] = {}

    def addEdge(self, n1, n2):
        w = self.widgets.get(n1)
        if w is not None:
            w.addEdge(n1, n2)
            return

        lst = EdgeEditorList()
        lst.addEdge(n1, n2)
        self.stack.addWidget(lst)
        self.widgets[n1] = lst

    def addItem(self, cond):
        for w in self.widgets.values():
            w.addItem(cond)

    def getItem(self, n1, n2):
        widget = self.widgets.get(n1)
        return widget.getItem(n2)

    def nodeChanged(self, n1):
        widget = self.widgets.get(n1)

        if widget is not None:
            self.stack.setCurrentWidget(widget)
