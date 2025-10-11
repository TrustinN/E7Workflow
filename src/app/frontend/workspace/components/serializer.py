from src.app.frontend.events import EventLog

from ..events import WKEvents
from .controller import WorkspaceController
from .repository import WorkspaceRepository


class WorkspaceSerializer:
    def __init__(
        self,
        controller: WorkspaceController,
        repository: WorkspaceRepository,
        eventLog: EventLog,
    ):
        self.repository = repository
        self.controller = controller
        self.eventLog = eventLog

    def export(self):
        workspaces = self.repository.getAllWorkspaces()

        for id in workspaces:
            config = self.controller.readWorkspace(id)
            self.repository.updateWorkspace(id, config)

        self.repository.exportWorkspaces()
        self.eventLog.processEvent(WKEvents.WK_EXPORTED)

    def restore(self):
        self.controller.clearState()
        self.repository.importWorkspaces()

        workspaces = self.repository.getAllWorkspaces()

        for id, data in workspaces.items():
            parentID = data.get("parentID")

            self.controller.createWorkspace(id, parentID)
            self.controller.updateWorkspace(id, data)

        self.eventLog.processEvent(WKEvents.WK_IMPORTED)
