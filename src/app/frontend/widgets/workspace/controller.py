from src.app.frontend.state import WorkspaceContext
from src.app.frontend.widgets.utils.colors import Alpha, Colors, with_alpha

from .view import WorkspaceView


class WorkspaceController:
    def __init__(self, context: WorkspaceContext, view: WorkspaceView):
        self.context = context
        self.view = view

        self._loading = False
        self.view.workspacePressed_.connect(self.onWorkspacePressed)
        self.view.workspaceUpdate_.connect(self.onWorkspaceUpdate)

        self.context.selectionModel.selected_.connect(self.onSelection)

    def _createRootWorkspace(self, id, data):
        self.view.createRootWorkspace(id)
        self.view.setWorkspacePadding(id, 15)
        self.view.setWorkspaceName(id, data["text"])

    def _createChildWorkspace(self, id, parentID, data):
        name = f"{data["grouping"]} - {data["text"]}"

        self.view.createChildWorkspace(id, parentID)
        self.view.setWorkspaceName(id, name)

    def createWorkspace(self, id, parentID, data):
        if parentID is None:
            self._createRootWorkspace(id, data)

            data = self.view.getWorkspaceData(id)
            self.context.viewModel.createRoot(id, data)
        else:
            self._createChildWorkspace(id, parentID, data)

            data = self.view.getWorkspaceData(id)
            self.context.viewModel.createNode(id, parentID, data)

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

    def onWorkspacePressed(self, id):
        self.context.selectionModel.setSelected(id)

    def onWorkspaceUpdate(self, id: str):
        data = self.view.getWorkspaceData(id)

        if self._loading:
            return

        self.context.viewModel.updateNode(id, data)

    def rerenderView(self):
        for nodeID in self.context.viewModel.nodeIter():
            data = self.context.viewModel.nodeData(nodeID)
            self.view.restoreWorkspaceData(nodeID, data)

    def recreateView(self):
        self._loading = True

        for nodeID in self.context.wsTreeModel.nodeIter():
            data = self.context.wsTreeModel.nodeData(nodeID)

            if self.context.wsTreeModel.isRoot(nodeID):
                self._createRootWorkspace(nodeID, data)
            else:
                parentID = self.context.wsTreeModel.parent(nodeID)
                self._createChildWorkspace(nodeID, parentID, data)

        self.rerenderView()
        self._loading = False

    def clearState(self):
        rootID = self.context.wsTreeModel.root
        self.view.clear(rootID)

        self.context.viewModel.clear()
        self._loading = False
