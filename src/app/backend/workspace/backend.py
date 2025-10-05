from nanoid import generate


class WorkspaceBackend:
    def __init__(self):
        self.workspaces = {}

    def createWorkspace(self, userData=None):
        userData = userData or {}

        workspaceID = generate()
        self.workspaces[workspaceID] = userData
        return workspaceID, userData

    def updateWorkspace(self, id, data):
        self.workspaces[id].update(data)

    def clear(self):
        self.workspaces.clear()

    def overwrite(self, data):
        self.workspaces = data
