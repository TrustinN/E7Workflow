from functools import partial

from PyQt5.QtCore import QObject, pyqtSignal

from src.app.frontend.state import SelectionModel
from src.app.frontend.workspace.components import Workspace
from src.app.frontend.workspace.components.utils.colors import Alpha, Colors, with_alpha

from .model import TreeModel


class WorkspaceView(QObject):
    workspaceCreated_ = pyqtSignal(str)

    def __init__(
        self,
        model: TreeModel,
        viewModel: TreeModel,
        selectionModel: SelectionModel,
    ):
        super().__init__()
        self.model = model
        self.viewModel = viewModel
        self.selectionModel = selectionModel

        self.workspaces: dict[str, Workspace] = {}

        self.model.nodeCreated_.connect(self.createWorkspace)
        self.model.modelClear_.connect(self.clearState)
        self.selectionModel.selected_.connect(self.onSelection)

        self.workspaceCreated_.connect(self.viewModelWorkspaceCreate)
        self.viewModel.modelReset_.connect(self.onViewModelReset)

    def createWorkspace(self, id):
        workspace = Workspace()
        workspace.show()
        workspace.unlock()

        workspaceData = self.model.nodeData(id)
        workspace.setName(workspaceData["text"])

        onWorkspacePressed = partial(self.onWorkspacePressed, id)
        workspace.mousePress.connect(onWorkspacePressed)

        onWorkspaceUpdate = partial(self.viewModelWorkspaceUpdate, id)
        workspace.resizeSignal.connect(onWorkspaceUpdate)
        workspace.moveSignal.connect(onWorkspaceUpdate)

        self.workspaces[id] = workspace
        parentID = self.model.parent(id)

        if parentID:
            self.workspaces[parentID].addChild(workspace)
        else:
            workspace.setPadding(15)

        self.workspaceCreated_.emit(id)

    def viewModelWorkspaceCreate(self, id: str):
        parentID = self.model.parent(id)
        workspace = self.workspaces[id]
        data = workspace.getData()

        if parentID is None:
            self.viewModel.createRoot(id, data)
        else:
            self.viewModel.createNode(id, parentID, data)

    def viewModelWorkspaceUpdate(self, id: str):
        workspace = self.workspaces[id]
        data = workspace.getData()
        self.viewModel.updateNode(id, data)

    def onWorkspacePressed(self, id):
        self.selectionModel.setSelected(id)

    def onSelection(self, id):
        prevID = self.selectionModel.getPrevSelected()
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
        for workspace in self.workspaces.values():
            workspace.blockSignals(True)

        for nodeID in self.viewModel.nodeIter():
            data = self.viewModel.nodeData(nodeID)
            workspace = self.workspaces[nodeID]
            workspace.setData(data)

        for workspace in self.workspaces.values():
            workspace.blockSignals(False)

    def clearState(self):
        rootID = self.model.root
        rootWorkspace = self.workspaces[rootID]
        rootWorkspace.deleteLater()

        self.workspaces.clear()
