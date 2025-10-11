from src.app.frontend.context import Context
from src.app.frontend.events import AppEvents, EventHandler, EventLog
from src.router.routing import Dispatcher

from .components import (
    WorkspaceBuilder,
    WorkspaceController,
    WorkspaceRepository,
    WorkspaceSerializer,
    WorkspaceView,
)
from .events import WKEvents
from .widget import WorkspaceWidget


class WorkspaceCore:
    def __init__(
        self,
        widget: WorkspaceWidget,
        context: Context,
        eventLog: EventLog,
        dispatcher: Dispatcher,
    ):
        self.view = WorkspaceView()
        self.view.workspacePressed_.connect(self.onWorkspaceFocused)

        self.controller = WorkspaceController()
        self.controller.setView(self.view)

        self.context = context

        self.repository = WorkspaceRepository(dispatcher)
        self.builder = WorkspaceBuilder(self.controller, self.repository)
        self.serializer = WorkspaceSerializer(
            self.controller, self.repository, eventLog
        )

        self.widget = widget
        self.widget.createWorkspaceBtn.clicked.connect(self.onWorkspaceCreated)
        self.widget.restoreWorkspaceBtn.clicked.connect(self.context.load)
        self.widget.restoreWorkspaceBtn.clicked.connect(self.serializer.restore)
        self.widget.exportWorkspaceBtn.clicked.connect(self.context.save)
        self.widget.exportWorkspaceBtn.clicked.connect(self.serializer.export)

        self.eventLog = eventLog

        loadedHandler = EventHandler(lambda data: self._createRootWorkspace())
        self.eventLog.register(AppEvents.APP_LOADED, loadedHandler)

    def _createRootWorkspace(self):
        id = self.builder.create()
        self.eventLog.processEvent(WKEvents.WK_CREATED_ROOT, {"id": id})

        data = {"id": id, "padding": 15, "text": "Root"}
        self.builder.update(id, data)
        self.eventLog.processEvent(WKEvents.WK_UPDATED, data)

    def onWorkspaceCreated(self):
        parentID = self.view.focusedWorkspace
        id = self.builder.create(parentID)
        self.eventLog.processEvent(WKEvents.WK_CREATED, {"id": id})

        name = self.widget.getWorkspaceName()
        data = {"id": id, "text": name, "parentID": parentID}
        self.builder.update(id, data)
        self.eventLog.processEvent(WKEvents.WK_UPDATED, data)

    def onWorkspaceFocused(self, id):
        self.eventLog.processEvent(WKEvents.WK_FOCUSED, {"id": id})
