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
        self.widget = widget
        self.controller = controller
        self.eventLog = eventLog

        self.eventLog.register(EventType.APPLICATION_LOADED, self._createRootWorkspace)
        self.widget.createWorkspaceBtn.clicked.connect(self.onWorkspaceCreated)

    def _createRootWorkspace(self, data):
        id = self.controller.createWorkspace(self.view)
        self.controller.setFocusedWorkspace(self.view, id)

        self.controller.updateWorkspace(
            self.view, {"id": id, "padding": 15, "text": "Root"}
        )

    def onWorkspaceCreated(self):
        id = self.controller.createWorkspace(self.view)

        name = self.widget.getWorkspaceName()
        self.controller.updateWorkspace(self.view, {"id": id, "text": name})
