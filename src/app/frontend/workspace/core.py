from src.app.backend.workspace.service import ws
from src.app.frontend.context import Context
from src.app.frontend.events import EventLog, EventType
from src.router.routing import Client, Dispatcher, Link

from .controller import WorkspaceController
from .view import WorkspaceView
from .widget import WorkspaceWidget


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
        self.eventLog.processEvent(EventType.WORKSPACE_EXPORTED)

    def restore(self):
        self.controller.clearState()
        self.repository.importWorkspaces()

        workspaces = self.repository.getAllWorkspaces()

        for id, data in workspaces.items():
            parentID = data.get("parentID")

            self.controller.createWorkspace(id, parentID)
            self.controller.updateWorkspace(id, data)

        self.eventLog.processEvent(EventType.WORKSPACE_IMPORTED)


class WorkspaceBuilder:
    def __init__(
        self,
        controller: WorkspaceController,
        repository: WorkspaceRepository,
        eventLog: EventLog,
    ):
        self.repository = repository
        self.eventLog = eventLog
        self.controller = controller

    def create(self, parentID=None):
        id = self.repository.createWorkspace()
        self.controller.createWorkspace(id, parentID)
        self.eventLog.processEvent(EventType.WORKSPACE_CREATED, {"id": id})

        return id

    def update(self, id, data):
        self.repository.updateWorkspace(id, data)
        self.controller.updateWorkspace(id, data)
        self.eventLog.processEvent(EventType.WORKSPACE_UPDATED, data)


class WorkspaceCore:
    def __init__(
        self,
        widget: WorkspaceWidget,
        controller: WorkspaceController,
        context: Context,
        eventLog: EventLog,
        dispatcher: Dispatcher,
    ):
        self.view = WorkspaceView()
        self.view.workspacePressed_.connect(self.onWorkspaceFocused)

        self.controller = controller
        self.controller.setView(self.view)

        self.context = context

        self.repository = WorkspaceRepository(dispatcher)
        self.builder = WorkspaceBuilder(controller, self.repository, eventLog)
        self.serializer = WorkspaceSerializer(controller, self.repository, eventLog)

        self.widget = widget
        self.widget.createWorkspaceBtn.clicked.connect(self.onWorkspaceCreated)
        self.widget.restoreWorkspaceBtn.clicked.connect(self.context.load)
        self.widget.restoreWorkspaceBtn.clicked.connect(self.serializer.restore)
        self.widget.exportWorkspaceBtn.clicked.connect(self.context.save)
        self.widget.exportWorkspaceBtn.clicked.connect(self.serializer.export)

        self.eventLog = eventLog
        self.eventLog.register(EventType.APPLICATION_LOADED, self._createRootWorkspace)

    def _createRootWorkspace(self, data):
        id = self.builder.create()

        data = {"id": id, "padding": 15, "text": "Root"}
        self.builder.update(id, data)

    def onWorkspaceCreated(self):
        parentID = self.view.focusedWorkspace
        id = self.builder.create(parentID)

        name = self.widget.getWorkspaceName()
        data = {"id": id, "text": name, "parentID": parentID}
        self.builder.update(id, data)

    def onWorkspaceFocused(self, id):
        self.eventLog.processEvent(EventType.WORKSPACE_FOCUSED, {"id": id})
