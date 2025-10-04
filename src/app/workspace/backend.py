from nanoid import generate


class WorkspaceBackend:
    def __init__(self):
        self.workspaces = {}

    def createWorkspace(self, userData=None):
        if userData is None:
            userData = {}

        workspaceID = generate()
        self.workspaces[workspaceID] = userData
        return workspaceID, userData

    def updateWorkspace(self, id, data):
        self.workspaces[id].update(data)

    def clear(self):
        self.workspaces.clear()
