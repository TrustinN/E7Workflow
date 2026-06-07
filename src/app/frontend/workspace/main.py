from PyQt5.QtWidgets import QVBoxLayout, QWidget

from .mvc import TreeModel, WorkspaceView
from .node import WorkspaceNode
from .widgets import WorkspaceButtons


class WorkspaceComponent(QWidget):
    def __init__(self, selectionModel):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.buttons = WorkspaceButtons()

        self.workspaceModel = TreeModel()
        self.viewModel = TreeModel()
        self.selectionModel = selectionModel

        self.node = WorkspaceNode(self.workspaceModel, self.selectionModel)
        self.view = WorkspaceView(
            self.workspaceModel, self.viewModel, self.selectionModel
        )

        self.buttons.createWorkspace_.connect(self.node.createWorkspace)
        # self.buttons.exportBtn.clicked.connect(self.workspaceExport)
        # self.buttons.importBtn.clicked.connect(self.workspaceImport)
        self.layout.addWidget(self.buttons)
