from src.router.routing import Client, Dispatcher, Link

from .service import ws
from .view import WorkspaceView


class WorkspaceController:
    def __init__(self, dispatcher: Dispatcher):
        self.client = Client("Workspace Controller", dispatcher)

    def setView(self, view: WorkspaceView):
        self.view = view

    def createWorkspace(self):
        response = self.client.post(Link(ws.NAME, ws.WORKSPACE))
        id = response["workspaceID"]
        self.view.createWorkspace(id)

        return id

    def updateWorkspace(self, data):
        id = data.get("id")
        self.client.put(Link(ws.NAME, ws.WORKSPACE, id), data)
        self.view.updateWorkspace(id, data)
