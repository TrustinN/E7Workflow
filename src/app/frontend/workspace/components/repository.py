from src.app.backend.workspace.service import ws
from src.router.routing import Client, Dispatcher, Link


class WorkspaceRepository:
    def __init__(self, dispatcher: Dispatcher):
        self.client = Client("Workspace Repository", dispatcher)

    def createWorkspace(self):
        link = Link(ws.NAME, ws.WORKSPACE)
        response = self.client.post(link)
        id = response["workspaceID"]
        return id

    def updateWorkspace(self, id, data):
        link = Link(ws.NAME, ws.WORKSPACE, id)
        self.client.put(link, data)

    def getAllWorkspaces(self):
        link = Link(ws.NAME, ws.WORKSPACE)
        workspaces = self.client.get(link)
        return workspaces

    def exportWorkspaces(self):
        link = Link(ws.NAME, ws.WORKSPACE, ws.EXPORT)
        self.client.post(link)

    def importWorkspaces(self):
        link = Link(ws.NAME, ws.WORKSPACE, ws.IMPORT)
        self.client.post(link)
