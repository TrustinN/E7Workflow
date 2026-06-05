from .view import WorkspaceView


class WorkspaceController:
    def __init__(self, view: WorkspaceView):
        self.view = view

    def clearState(self):
        if self.view:
            self.view.clearState()

    def createWorkspace(self, id, parentID=None):
        self.view.createWorkspace(id, parentID)

    def readWorkspace(self, id):
        return self.view.readWorkspace(id)

    def workspaces(self):
        return self.view.allWorkspaces()

    def updateWorkspace(self, id, data):
        self.view.updateWorkspace(id, data)
