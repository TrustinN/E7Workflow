import json

from src.router.routing import Client, Dispatcher, Link

from ..event.events import EventLog, EventType
from .controller import WorkspaceController
from .service import ws
from .view import WorkspaceView
from .widget import WorkspaceWidget


class WorkspaceCore:
    def __init__(
        self,
        widget: WorkspaceWidget,
        controller: WorkspaceController,
        eventLog: EventLog,
        dispatcher: Dispatcher,
    ):
        self.client = Client("Workspace Controller", dispatcher)

        self.view = WorkspaceView()
        self.view.workspacePressed_.connect(self.onWorkspaceFocused)

        self.controller = controller
        self.controller.setView(self.view)

        self.widget = widget
        self.widget.createWorkspaceBtn.clicked.connect(self.onWorkspaceCreated)
        self.widget.restoreWorkspaceBtn.clicked.connect(self.onWorkspaceRestore)
        self.widget.exportWorkspaceBtn.clicked.connect(self.onWorkspaceExport)

        self.eventLog = eventLog
        self.eventLog.register(EventType.APPLICATION_LOADED, self._createRootWorkspace)

    def _createRootWorkspace(self, data):
        response = self.client.post(Link(ws.NAME, ws.WORKSPACE))
        id = response["workspaceID"]
        self.controller.createWorkspace(id)
        self.eventLog.processEvent(EventType.WORKSPACE_CREATED, {"id": id})

        data = {"id": id, "padding": 15, "text": "Root"}
        self.client.put(Link(ws.NAME, ws.WORKSPACE, id), data)
        self.controller.updateWorkspace(id, data)
        self.eventLog.processEvent(EventType.WORKSPACE_UPDATED, data)

    def onWorkspaceCreated(self):
        response = self.client.post(Link(ws.NAME, ws.WORKSPACE))
        id = response["workspaceID"]
        parentID = self.view.focusedWorkspace
        self.controller.createWorkspace(id, parentID)
        self.eventLog.processEvent(EventType.WORKSPACE_CREATED, {"id": id})

        name = self.widget.getWorkspaceName()
        data = {"id": id, "text": name, "parentID": parentID}
        self.client.put(Link(ws.NAME, ws.WORKSPACE, id), data)
        self.controller.updateWorkspace(id, data)
        self.eventLog.processEvent(EventType.WORKSPACE_UPDATED, data)

    def onWorkspaceFocused(self, id):
        self.eventLog.processEvent(EventType.WORKSPACE_FOCUSED, {"id": id})

    def onWorkspaceExport(self):
        workspaces = self.client.get(Link(ws.NAME, ws.WORKSPACE))

        for id in workspaces:
            config = self.controller.readWorkspace(id)
            self.client.put(Link(ws.NAME, ws.WORKSPACE, id), config)

        self.client.post(Link(ws.NAME, ws.WORKSPACE, ws.EXPORT))

    def onWorkspaceRestore(self):
        self.controller.clearState()

        with open("workspaceConfig", "r") as f:
            workspaces = json.load(f)

            for id in workspaces:
                data = workspaces[id]
                parentID = data.get("parentID")

                self.controller.createWorkspace(id, parentID)
                self.controller.updateWorkspace(id, data)
