from nanoid import generate


class WorkspaceBackend:
    def __init__(self):
        self.workspaces = {}

    def createWorkspace(self, parentID, userData=None):
        if userData is None:
            userData = {}

        workspaceID = generate()
        data = {"parentID": parentID, "data": userData}
        self.workspaces[workspaceID] = data
        return workspaceID, data

    def updateWorkspace(self, id, data):
        wsData = self.workspaces[id]
        wsData["data"].update(data)
