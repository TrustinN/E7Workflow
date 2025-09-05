from dataclasses import asdict

from .model import WorkspaceData, WorkspaceTreeModel
from .view import WorkspaceView


class WorkspaceController:
    def __init__(self, model: WorkspaceTreeModel, view: WorkspaceView):
        self.model = model
        self.view = view

        self.signalOriginView = False

        self.model.workspaceCreated_.connect(self.onWorkspaceCreated)
        self.model.workspaceUpdated_.connect(self.onWorkspaceUpdated)

        self.view.workspacePressed_.connect(self.onWorkspaceFocused)

    def onWorkspaceCreated(self, id, data: WorkspaceData):
        self.view.createWorkspace(id)
        self.view.updateWorkspace(id, asdict(data))

    def onWorkspaceUpdated(self, id, data: WorkspaceData):
        if self.signalOriginView:
            return
        self.view.updateWorkspace(id, asdict(data))

    def onWorkspaceFocused(self, id):
        self.signalOriginView = True
        self.model.setFocusedWorkspace(id)
        self.signalOriginView = False

    def focusedWorkspace(self):
        return self.model.focusedWorkspace()
