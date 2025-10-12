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


class WorkspaceComponent:
    def __init__(
        self,
        ctxManager: ContextManager,
        eventLog: EventLog,
        dispatcher: Dispatcher,
    ):
        self.ctxManager = ctxManager
        self.eventLog = eventLog

        self.widget = WorkspaceWidget()

        self.repository = WorkspaceRepository(dispatcher)
        self.wkUI = WorkspaceUI(self.widget, self.repository)
        self.guiCpt = WorkspaceUIComponent(self.wkUI)

        self.serializer = WorkspaceSerializer(self.wkUI)
        self.serialCpt = WorkspaceSerializerComponent(self.serializer)

        capabilities = self._getCapabilities()
        self._initSignals()
        self._createHandlers(capabilities)
        self._bindSignals()

    def _bindSignals(self):
        signalNames = ["create", "restore", "export", "focused"]

        for name in signalNames:
            signal = self.signals.get(f"{name}Signal")
            handler = self.handlers.get(f"{name}Handler")

            signal.setCallback(handler)

        loadedHandler = self.handlers.get("loadedHandler")
        self.eventLog.register(AppEvents.APP_LOADED, loadedHandler)

    def _createHandlers(self, capabilities):
        createWkUI = capabilities.get("createWk")
        updateWkUI = capabilities.get("updateWk")
        getWkNameUI = capabilities.get("getWkName")
        serialImport = capabilities.get("serialImport")
        serialExport = capabilities.get("serialExport")

        createHandler = EventHandler(createWkUI)
        createHandler.chain(emitHandler(self.eventLog, WKEvents.WK_CREATED))
        createHandler.chain(getWkNameUI)
        createHandler.chain(updateWkUI)
        createHandler.chain(emitHandler(self.eventLog, WKEvents.WK_UPDATED))

        restoreHandler = EventHandler(serialImport, data=False)
        restoreHandler.chain(self.ctxManager.loadContext, data=False)
        restoreHandler.chain(emitHandler(self.eventLog, WKEvents.WK_IMPORTED))

        exportHandler = EventHandler(serialExport, data=False)
        exportHandler.chain(self.ctxManager.saveContext, data=False)
        exportHandler.chain(emitHandler(self.eventLog, WKEvents.WK_EXPORTED))

        focusedHandler = EventHandler(emitHandler(self.eventLog, WKEvents.WK_FOCUSED))

        loadedHandler = EventHandler(createWkUI)
        loadedHandler.chain(emitHandler(self.eventLog, WKEvents.WK_CREATED_ROOT))
        loadedHandler.chain(inject(lambda: {"padding": 15, "text": "Root"}))
        loadedHandler.chain(updateWkUI)
        loadedHandler.chain(emitHandler(self.eventLog, WKEvents.WK_UPDATED))

        self.handlers = {
            "createHandler": createHandler,
            "restoreHandler": restoreHandler,
            "exportHandler": exportHandler,
            "focusedHandler": focusedHandler,
            "loadedHandler": loadedHandler,
        }

    def _initSignals(self):

        idFormatter = JsonFormatter(["id"])

        createSignal = EventSignal(self.wkUI.workspaceCreated_.connect)
        restoreSignal = EventSignal(self.wkUI.workspaceImport_.connect)
        exportSignal = EventSignal(self.wkUI.workspaceExport_.connect)
        focusedSignal = EventSignal(self.wkUI.workspacePressed_.connect)

        focusedSignal.setFormatter(idFormatter)

        self.signals = {
            "createSignal": createSignal,
            "restoreSignal": restoreSignal,
            "exportSignal": exportSignal,
            "focusedSignal": focusedSignal,
        }

    def _getCapabilities(self):
        createWkUI = self.guiCpt.useAction(self.guiCpt.CREATE_WK)
        updateWkUI = self.guiCpt.useAction(self.guiCpt.UPDATE_WK)
        getWkNameUI = self.guiCpt.useAction(self.guiCpt.GET_WK_NAME)

        serialImport = self.serialCpt.useAction(self.serialCpt.IMPORT)
        serialExport = self.serialCpt.useAction(self.serialCpt.EXPORT)

        return {
            "createWk": createWkUI,
            "updateWk": updateWkUI,
            "getWkName": getWkNameUI,
            "serialImport": serialImport,
            "serialExport": serialExport,
        }
