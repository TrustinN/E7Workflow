from functools import partial

from src.app.frontend.state import SelectionModel
from src.app.frontend.workspace.components import Workspace
from src.app.frontend.workspace.components.utils.colors import Alpha, Colors, with_alpha

from .model import TreeModel


class WorkspaceView:

    def __init__(
        self,
        model: TreeModel,
        viewModel: TreeModel,
        selectionModel: SelectionModel,
    ):
        self.model = model
        self.viewModel = viewModel
        self.selectionModel = selectionModel

        self.workspaces: dict[str, Workspace] = {}

        self.model.nodeCreated_.connect(self.createWorkspace)
        self.selectionModel.selected_.connect(self.onSelection)

    def createWorkspace(self, id):
        workspace = Workspace()
        workspace.show()
        workspace.unlock()

        self.workspaces[id] = workspace
        parentID = self.model.parentNode(id)

        if parentID:
            self.workspaces[parentID].addChild(workspace)
        else:
            workspace.setPadding(15)

        workspaceData = self.model.nodeData(id)
        workspace.setName(workspaceData["text"])

        onWorkspacePressed = partial(self.onWorkspacePressed, id)
        workspace.mousePress.connect(onWorkspacePressed)

    def onWorkspacePressed(self, id):
        self.selectionModel.setSelected(id)

    def onSelection(self, id):
        prevID = self.selectionModel.getPrevSelected()
        if prevID:
            workspace = self.workspaces[prevID]
            workspace.setColor(Colors.DEFAULT_COLOR, Colors.DEFAULT_BORDER)

        workspace = self.workspaces[id]
        workspace.setColor(
            with_alpha(Colors.SKY_BLUE, Alpha.LIGHT),
            with_alpha(Colors.SKY_BLUE, Alpha.MEDIUM),
        )

    def clearState(self):
        rootID = self.model.root
        rootWorkspace = self.workspaces[rootID]
        rootWorkspace.deleteLater()

        self.workspaces.clear()
