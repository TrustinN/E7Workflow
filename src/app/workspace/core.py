from ..event.events import EventLog, EventType
from .controller import WorkspaceController
from .view import WorkspaceView
from .widget import WorkspaceWidget


class WorkspaceCore:
    def __init__(
        self,
        widget: WorkspaceWidget,
        controller: WorkspaceController,
        eventLog: EventLog,
    ):
        self.view = WorkspaceView()
        self.view.workspacePressed_.connect(self.onWorkspaceFocused)

        self.controller = controller
        self.controller.setView(self.view)

        self.widget = widget
        self.widget.createWorkspaceBtn.clicked.connect(self.onWorkspaceCreated)

        self.eventLog = eventLog
        self.eventLog.register(EventType.APPLICATION_LOADED, self._createRootWorkspace)

    def _createRootWorkspace(self, data):
        id = self.controller.createWorkspace()
        self.eventLog.processEvent(EventType.WORKSPACE_CREATED, {"id": id})

        data = {"id": id, "padding": 15, "text": "Root"}
        self.controller.updateWorkspace(data)
        self.eventLog.processEvent(EventType.WORKSPACE_UPDATED, data)

    def onWorkspaceCreated(self):
        id = self.controller.createWorkspace()
        self.eventLog.processEvent(EventType.WORKSPACE_CREATED, {"id": id})

        name = self.widget.getWorkspaceName()
        data = {"id": id, "text": name}
        self.controller.updateWorkspace(data)
        self.eventLog.processEvent(EventType.WORKSPACE_UPDATED, data)

    def onWorkspaceFocused(self, id):
        self.eventLog.processEvent(EventType.WORKSPACE_FOCUSED, {"id": id})
