from PyQt5.QtWidgets import QTabWidget

from src.app.components.runner.model import RunnerModel
from src.app.components.script import CodeEditor
from src.app.state import Context, Selection, SelectionType


class ActionEditor(QTabWidget):
    def __init__(self, context: Context, model: RunnerModel):
        super().__init__()

        self.model = model
        self.context = context

        self.preActionEditor = CodeEditor()
        self.postActionEditor = CodeEditor()

        self.addTab(self.preActionEditor, "Pre-Action")
        self.addTab(self.postActionEditor, "Post-Action")

        self.context.selectionModel.selected_.connect(self.onSelectionChanged)
        self.preActionEditor.textChanged.connect(self.updateNodePreAction)
        self.postActionEditor.textChanged.connect(self.updateNodePostAction)

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
