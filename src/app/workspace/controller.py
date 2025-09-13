# from .model import WorkspaceData, WorkspaceTreeModel
from .view import WorkspaceView


class WorkspaceController:
    def __init__(self, view: WorkspaceView):
        self.state = {"focusedWorkspace": None}
        self.view = view

        self.view.workspacePressed_.connect(self.setFocusedWorkspace)

    def createWorkspace(self, id, parentID, data):
        self.view.createWorkspace(id)
        self.view.updateWorkspace(id, data)

    def updateWorkspace(self, id, data):
        self.view.updateWorkspace(id, data)

    def focusedWorkspace(self):
        return self.state["focusedWorkspace"]

    def setFocusedWorkspace(self, id):
        self.state["focusedWorkspace"] = id
