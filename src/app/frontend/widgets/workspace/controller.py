from src.app.frontend.state import WorkspaceContext
from src.app.frontend.widgets.workspace.components.utils.colors import (
    Alpha,
    Colors,
    with_alpha,
)

from .view import WorkspaceView


class WorkspaceController:
    def __init__(self, context: WorkspaceContext, view: WorkspaceView):
        self.context = context
        self.view = view

        self.view.workspacePressed_.connect(self.onWorkspacePressed)
        self.view.workspaceCreated_.connect(self.viewModelWorkspaceCreate)
        self.view.workspaceUpdate_.connect(self.viewModelWorkspaceUpdate)

        self.context.wsTreeModel.nodeCreated_.connect(self.onWorkspaceCreate)
        self.context.wsTreeModel.modelClear_.connect(self.clearState)
        self.context.selectionModel.selected_.connect(self.onSelection)
        self.context.viewModel.modelReset_.connect(self.onViewModelReset)

    def _createRootWorkspace(self, data):
        self.view.createRootWorkspace(data["id"])
        self.view.setWorkspacePadding(data["id"], 15)
        self.view.setWorkspaceName(data["id"], data["text"])

    def _createChildWorkspace(self, data):
        name = f"{data["grouping"]} - {data["text"]}"

        self.view.createChildWorkspace(data["id"], data["parentID"])
        self.view.setWorkspaceName(data["id"], name)

    def onWorkspaceCreate(self, id):
        data = self.context.wsTreeModel.nodeData(id)
        if self.context.wsTreeModel.isRoot(id):
            self._createRootWorkspace(data)
        else:
            self._createChildWorkspace(data)

    def onWorkspacePressed(self, id):
        self.context.selectionModel.setSelected(id)

    def onSelection(self, id):
        prevID = self.context.selectionModel.getPrevSelected()
        if prevID:
            self.view.setWorkspaceColor(
                prevID,
                Colors.DEFAULT_COLOR,
                Colors.DEFAULT_BORDER,
            )

        if id:
            self.view.setWorkspaceColor(
                id,
                with_alpha(Colors.SKY_BLUE, Alpha.LIGHT),
                with_alpha(Colors.SKY_BLUE, Alpha.MEDIUM),
            )

    def viewModelWorkspaceCreate(self, id: str):
        data = self.view.getWorkspaceData(id)

        if self.context.wsTreeModel.isRoot(id):
            self.context.viewModel.createRoot(id, data)
        else:
            parentID = self.context.wsTreeModel.parent(id)
            self.context.viewModel.createNode(id, parentID, data)

    def viewModelWorkspaceUpdate(self, id: str):
        data = self.view.getWorkspaceData(id)
        self.context.viewModel.updateNode(id, data)

    def onViewModelReset(self):
        for nodeID in self.context.viewModel.nodeIter():
            data = self.context.viewModel.nodeData(nodeID)
            self.view.restoreWorkspaceData(nodeID, data)

    def clearState(self):
        rootID = self.context.wsTreeModel.root
        self.view.clear(rootID)
