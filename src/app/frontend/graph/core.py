from src.app.frontend.context import ContextManager
from src.app.frontend.events import EventHandler, EventLog, inject
from src.app.frontend.workspace.events import WKEvents
from src.router.routing import Dispatcher

from .components import (
    GraphRepository,
    GraphSerializer,
    GraphSerializerComponent,
    GraphUI,
    GraphUIComponent,
)
from .context import GRAPH_CTX, GraphContextManager
from .widget import GraphWidget


class GraphCore:
    def __init__(
        self,
        widget: GraphWidget,
        ctxManager: ContextManager,
        eventLog: EventLog,
        dispatcher: Dispatcher,
    ):
        self.widget = widget

        context = ctxManager.addContext(GRAPH_CTX)
        self.ctxManager = GraphContextManager(context)

        self.repository = GraphRepository(dispatcher)

        self.graphUI = GraphUI(self.widget, self.repository)
        self.guiCpt = GraphUIComponent(self.graphUI)

        self.serializer = GraphSerializer(self.graphUI)
        self.serialCpt = GraphSerializerComponent(self.serializer)

        self.eventLog = eventLog

        handlers = self._createHandlers()
        for event, handler in handlers.items():
            self.eventLog.register(event, handler)

    def _createHandlers(self):
        capabilities = self._getCapabilities()
        createGraphUI = capabilities.get("createGraph")
        createNodeUI = capabilities.get("createNode")
        createEdgeUI = capabilities.get("createEdge")
        updateNodeUI = capabilities.get("updateNode")
        setSceneUI = capabilities.get("setScene")
        serialImport = capabilities.get("serialImport")
        serialExport = capabilities.get("serialExport")

        createRootHandler = EventHandler(inject(self.ctxManager.getData))
        createRootHandler.chain(createGraphUI)
        createRootHandler.chain(self.ctxManager.updateSceneBinding)
        createRootHandler.chain(self.ctxManager.updateActiveScene)

        createdHandler = EventHandler(inject(self.ctxManager.getData))
        createdHandler.chain(createGraphUI)
        createdHandler.chain(self.ctxManager.updateSceneBinding)
        createdHandler.chain(createNodeUI)
        createdHandler.chain(self.ctxManager.updateNodeBinding)
        createdHandler.chain(self.ctxManager.updateSceneParents)

        updatedHandler = EventHandler(inject(self.ctxManager.getData))
        updatedHandler.chain(updateNodeUI)

        focusedHandler = EventHandler(inject(self.ctxManager.getData))
        focusedHandler.chain(setSceneUI)

        importHandler = EventHandler(serialImport, data=False)

        exportHandler = EventHandler(serialExport, data=False)

        return {
            WKEvents.WK_CREATED_ROOT: createRootHandler,
            WKEvents.WK_CREATED: createdHandler,
            WKEvents.WK_UPDATED: updatedHandler,
            WKEvents.WK_FOCUSED: focusedHandler,
            WKEvents.WK_IMPORTED: importHandler,
            WKEvents.WK_EXPORTED: exportHandler,
        }

    def _getCapabilities(self):
        createGraphUI = self.guiCpt.useAction(self.guiCpt.CREATE_GRAPH)
        createNodeUI = self.guiCpt.useAction(self.guiCpt.CREATE_NODE)
        createEdgeUI = self.guiCpt.useAction(self.guiCpt.CREATE_EDGE)
        updateNodeUI = self.guiCpt.useAction(self.guiCpt.UPDATE_NODE)
        setSceneUI = self.guiCpt.useAction(self.guiCpt.SET_SCENE)

        serialImport = self.serialCpt.useAction(self.serialCpt.IMPORT)
        serialExport = self.serialCpt.useAction(self.serialCpt.EXPORT)

        return {
            "createGraph": createGraphUI,
            "createNode": createNodeUI,
            "createEdge": createEdgeUI,
            "updateNode": updateNodeUI,
            "setScene": setSceneUI,
            "serialImport": serialImport,
            "serialExport": serialExport,
        }
