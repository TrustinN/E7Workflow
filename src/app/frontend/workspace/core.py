from src.app.frontend.components import JsonFormatter
from src.app.frontend.context import ContextManager
from src.app.frontend.events import (
    AppEvents,
    EventHandler,
    EventLog,
    EventSignal,
    emitHandler,
    inject,
)
from src.router.routing import Dispatcher

from .components import (
    WorkspaceRepository,
    WorkspaceSerializer,
    WorkspaceSerializerComponent,
    WorkspaceUI,
    WorkspaceUIComponent,
)
from .events import WKEvents
from .widget import WorkspaceWidget


class WorkspaceCore:
    def __init__(
        self,
        widget: WorkspaceWidget,
        ctxManager: ContextManager,
        eventLog: EventLog,
        dispatcher: Dispatcher,
    ):

        self.ctxManager = ctxManager

        self.repository = WorkspaceRepository(dispatcher)
        self.wkUI = WorkspaceUI(widget, self.repository)
        self.guiCpt = WorkspaceUIComponent(self.wkUI)
        createWkUI = self.guiCpt.useAction(self.guiCpt.CREATE_WK)
        updateWkUI = self.guiCpt.useAction(self.guiCpt.UPDATE_WK)
        getWkNameUI = self.guiCpt.useAction(self.guiCpt.GET_WK_NAME)

        self.serializer = WorkspaceSerializer(self.wkUI)
        self.serialCpt = WorkspaceSerializerComponent(self.serializer)
        serialImport = self.serialCpt.useAction(self.serialCpt.IMPORT)
        serialExport = self.serialCpt.useAction(self.serialCpt.EXPORT)

        idFormatter = JsonFormatter(["id"])

        createSignal = EventSignal(self.wkUI.workspaceCreated_.connect)
        restoreSignal = EventSignal(self.wkUI.workspaceImport_.connect)
        exportSignal = EventSignal(self.wkUI.workspaceExport_.connect)
        focusedSignal = EventSignal(self.wkUI.workspacePressed_.connect)

        createHandler = EventHandler(createWkUI)
        createHandler.chain(emitHandler(eventLog, WKEvents.WK_CREATED))
        createHandler.chain(getWkNameUI)
        createHandler.chain(updateWkUI)
        createHandler.chain(emitHandler(eventLog, WKEvents.WK_UPDATED))

        restoreHandler = EventHandler(serialImport, data=False)
        restoreHandler.chain(self.ctxManager.loadContext, data=False)
        restoreHandler.chain(emitHandler(eventLog, WKEvents.WK_IMPORTED))

        exportHandler = EventHandler(serialExport, data=False)
        exportHandler.chain(self.ctxManager.saveContext, data=False)
        exportHandler.chain(emitHandler(eventLog, WKEvents.WK_EXPORTED))

        focusedHandler = EventHandler(emitHandler(eventLog, WKEvents.WK_FOCUSED))

        createSignal.setCallback(createHandler)
        restoreSignal.setCallback(restoreHandler)
        exportSignal.setCallback(exportHandler)
        focusedSignal.setCallback(focusedHandler, idFormatter)

        # self.widget.restoreWorkspaceBtn.clicked.connect(self.ctxManager.loadContext)
        # self.widget.restoreWorkspaceBtn.clicked.connect(self.serializer.restore)
        # self.widget.exportWorkspaceBtn.clicked.connect(self.ctxManager.saveContext)
        # self.widget.exportWorkspaceBtn.clicked.connect(self.serializer.export)

        self.eventLog = eventLog

        loadedHandler = EventHandler(createWkUI)
        loadedHandler.chain(emitHandler(eventLog, WKEvents.WK_CREATED_ROOT))
        loadedHandler.chain(inject(lambda: {"padding": 15, "text": "Root"}))
        loadedHandler.chain(updateWkUI)
        loadedHandler.chain(emitHandler(eventLog, WKEvents.WK_UPDATED))

        self.eventLog.register(AppEvents.APP_LOADED, loadedHandler)
