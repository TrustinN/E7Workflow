from functools import partial

from PyQt5.QtCore import QObject, pyqtSignal

from src.app.frontend.state import WorkspaceContext
from src.app.frontend.widgets.workspace.components import Workspace
from src.app.frontend.widgets.workspace.components.utils.colors import (
    Alpha,
    Colors,
    with_alpha,
)


class WorkspaceView(QObject):
    workspaceCreated_ = pyqtSignal(str)

    def __init__(self, context: WorkspaceContext):
        super().__init__()
        self.context = context

        self.workspaces: dict[str, Workspace] = {}

        self.context.wsTreeModel.nodeCreated_.connect(self.createWorkspace)
        self.context.wsTreeModel.modelClear_.connect(self.clearState)
        self.context.selectionModel.selected_.connect(self.onSelection)

        self.workspaceCreated_.connect(self.viewModelWorkspaceCreate)
        self.context.viewModel.modelReset_.connect(self.onViewModelReset)

    def createWorkspace(self, id):
        workspace = Workspace()
        workspace.show()
        workspace.unlock()

        onWorkspacePressed = partial(self.onWorkspacePressed, id)
        workspace.mousePress.connect(onWorkspacePressed)

        onWorkspaceUpdate = partial(self.viewModelWorkspaceUpdate, id)
        workspace.resizeSignal.connect(onWorkspaceUpdate)
        workspace.moveSignal.connect(onWorkspaceUpdate)

        self.workspaces[id] = workspace
        parentID = self.context.wsTreeModel.parent(id)

        data = self.context.wsTreeModel.nodeData(id)

        if parentID:
            self.workspaces[parentID].addChild(workspace)
            workspace.setName(f"{data["grouping"]} - {data["text"]}")
        else:
            workspace.setPadding(15)
            workspace.setName(data["text"])

        self.workspaceCreated_.emit(id)

    def viewModelWorkspaceCreate(self, id: str):
        parentID = self.context.wsTreeModel.parent(id)
        workspace = self.workspaces[id]
        data = workspace.getData()

        if parentID is None:
            self.context.viewModel.createRoot(id, data)
        else:
            self.context.viewModel.createNode(id, parentID, data)

    def viewModelWorkspaceUpdate(self, id: str):
        workspace = self.workspaces[id]
        data = workspace.getData()
        self.context.viewModel.updateNode(id, data)

    def onWorkspacePressed(self, id):
        self.context.selectionModel.setSelected(id)

    def onSelection(self, id):
        prevID = self.context.selectionModel.getPrevSelected()
        if prevID:
            workspace = self.workspaces[prevID]
            workspace.setColor(Colors.DEFAULT_COLOR, Colors.DEFAULT_BORDER)

        if id:
            workspace = self.workspaces[id]
            workspace.setColor(
                with_alpha(Colors.SKY_BLUE, Alpha.LIGHT),
                with_alpha(Colors.SKY_BLUE, Alpha.MEDIUM),
            )

    def onViewModelReset(self):
        for nodeID in self.context.viewModel.nodeIter():
            data = self.context.viewModel.nodeData(nodeID)
            workspace = self.workspaces[nodeID]
            workspace.restoreData(data)

    def clearState(self):
        rootID = self.context.wsTreeModel.root
        rootWorkspace = self.workspaces[rootID]
        rootWorkspace.deleteLater()

        self.workspaces.clear()
