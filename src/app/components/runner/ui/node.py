from PyQt5.QtWidgets import QFileDialog, QPushButton, QTabWidget, QVBoxLayout, QWidget

from src.app.components.runner.model import RunnerModel
from src.app.components.script import CodeEditor
from src.app.config import CUSTOM_ACTIONS_DIR
from src.app.state import Context, Selection, SelectionType


class ActionEditor(QTabWidget):
    def __init__(self, context: Context, model: RunnerModel):
        super().__init__()

        self.model = model
        self.context = context

        self.preActionEditor = CodeEditor()
        self.preImportBtn = QPushButton("Import")
        self.postActionEditor = CodeEditor()
        self.postImportBtn = QPushButton("Import")

        preActionWidget = QWidget()
        preActionLayout = QVBoxLayout(preActionWidget)
        preActionLayout.addWidget(self.preActionEditor)
        preActionLayout.addWidget(self.preImportBtn)

        postActionWidget = QWidget()
        postActionLayout = QVBoxLayout(postActionWidget)
        postActionLayout.addWidget(self.postActionEditor)
        postActionLayout.addWidget(self.postImportBtn)

        self.addTab(preActionWidget, "Pre-Action")
        self.addTab(postActionWidget, "Post-Action")

        self.context.selectionModel.selected_.connect(self.onSelectionChanged)
        self.preActionEditor.textChanged.connect(self.updateNodePreAction)
        self.postActionEditor.textChanged.connect(self.updateNodePostAction)
        self.preImportBtn.clicked.connect(self.onImportRequest)
        self.postImportBtn.clicked.connect(self.onImportRequest)

    def onSelectionChanged(self, selection: Selection):
        if not (selection.id and selection.type == SelectionType.WORKSPACE):
            self.preActionEditor.setText("")
            self.postActionEditor.setText("")
            self.preActionEditor.setReadOnly(True)
            self.postActionEditor.setReadOnly(True)
            return

        node = self.model.getNode(selection.id)
        self.preActionEditor.setText(node.preAction)
        self.postActionEditor.setText(node.postAction)
        self.preActionEditor.setReadOnly(False)
        self.postActionEditor.setReadOnly(False)

    def updateNodePreAction(self):
        selection = self.context.selectionModel.getSelected()
        if not (selection.id and selection.type == SelectionType.WORKSPACE):
            return

        self.model.updateNode(
            selection.id,
            {"preAction": self.preActionEditor.text()},
        )

    def updateNodePostAction(self):
        selection = self.context.selectionModel.getSelected()
        if not (selection.id and selection.type == SelectionType.WORKSPACE):
            return

        self.model.updateNode(
            selection.id,
            {"postAction": self.postActionEditor.text()},
        )

    def onImportRequest(self):
        selection = self.context.selectionModel.getSelected()
        if not (selection.id and selection.type == SelectionType.WORKSPACE):
            return

        path, _ = QFileDialog.getOpenFileName(self, "Load Action", CUSTOM_ACTIONS_DIR)

        if not path:
            return

        idx = self.currentIndex()
        content = ""
        with open(path, "r") as f:
            content = f.read()

        if idx == 0:
            self.preActionEditor.setText(content)
        else:

            self.postActionEditor.setText(content)
