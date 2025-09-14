from src.router.routing import Client, Dispatcher, Link

from ..event.events import Event, EventLog, EventType
from .service import ws
from .widget import WorkspaceWidget


class WorkspaceController:
    def __init__(
        self, eventLog: EventLog, dispatcher: Dispatcher, widget: WorkspaceWidget
    ):
        self.widget = widget
        self.client = Client("Workspace Controller", dispatcher)
        self.eventLog = eventLog

        self.widget.workspaceFocused_.connect(self.onWorkspaceFocused)
        self.eventLog.register(EventType.APPLICATION_LOADED, self._createRootWorkspace)

    def onWorkspaceFocused(self, id):
        self.eventLog.processEvent(Event(EventType.WORKSPACE_FOCUSED, {"id": id}))

    def _createRootWorkspace(self, data):
        response = self.client.post(Link(ws.NAME, ws.WORKSPACE))
        id = response["workspaceID"]
        self.widget.createWorkspace(id, name="Root")
        self.widget.setFocusedWorkspace(id)
        self.updateWorkspace(id, {"padding": 15, "text": "Root"})
        self.eventLog.processEvent(Event(EventType.WORKSPACE_CREATED, {"id": id}))

    def createWorkspace(self):
        parentID = self.widget.focusedWorkspace()

        response = self.client.post(Link(ws.NAME, ws.WORKSPACE), {"parentID": parentID})
        id = response["workspaceID"]
        self.widget.createWorkspace(id, parentID)
        self.eventLog.processEvent(Event(EventType.WORKSPACE_CREATED, {"id": id}))

    def updateWorkspace(self, id, data):
        self.client.put(Link(ws.NAME, ws.WORKSPACE, id), data)
        self.widget.updateWorkspace(id, data)
