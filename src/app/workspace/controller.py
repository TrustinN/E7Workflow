from src.router.routing import Client, Dispatcher, Link

from ..event.events import EventLog, EventType
from .service import ws
from .view import WorkspaceView


class WorkspaceController:
    def __init__(self, eventLog: EventLog, dispatcher: Dispatcher):
        self.eventLog = eventLog
        self.client = Client("Workspace Controller", dispatcher)

    def focusedWorkspace(self, view):
        return view.focusedWorkspace

    def setFocusedWorkspace(self, view, id):
        view.setFocusedWorkspace(id)
        self.eventLog.processEvent(EventType.WORKSPACE_FOCUSED, {"id": id})

    def createWorkspace(self, view: WorkspaceView):
        response = self.client.post(Link(ws.NAME, ws.WORKSPACE))
        id = response["workspaceID"]
        view.createWorkspace(id, view.focusedWorkspace)

        self.eventLog.processEvent(EventType.WORKSPACE_CREATED, {"id": id})

        return id

    def updateWorkspace(self, view, data):
        id = data.get("id")
        self.client.put(Link(ws.NAME, ws.WORKSPACE, id), data)
        view.updateWorkspace(id, data)

        self.eventLog.processEvent(EventType.WORKSPACE_UPDATED, data)
