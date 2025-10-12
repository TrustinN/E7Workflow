from src.app.frontend.context import Context, ContextManager
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
        createGraphUI = self.guiCpt.useAction(self.guiCpt.CREATE_GRAPH)
        createNodeUI = self.guiCpt.useAction(self.guiCpt.CREATE_NODE)
        createEdgeUI = self.guiCpt.useAction(self.guiCpt.CREATE_EDGE)
        updateNodeUI = self.guiCpt.useAction(self.guiCpt.UPDATE_NODE)
        setSceneUI = self.guiCpt.useAction(self.guiCpt.SET_SCENE)

        self.serializer = GraphSerializer(self.graphUI)
        self.serialCpt = GraphSerializerComponent(self.serializer)
        serialImport = self.serialCpt.useAction(self.serialCpt.IMPORT)
        serialExport = self.serialCpt.useAction(self.serialCpt.EXPORT)

        self.eventLog = eventLog

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

        self.eventLog.register(WKEvents.WK_CREATED_ROOT, createRootHandler)
        self.eventLog.register(WKEvents.WK_CREATED, createdHandler)
        self.eventLog.register(WKEvents.WK_UPDATED, updatedHandler)
        self.eventLog.register(WKEvents.WK_FOCUSED, focusedHandler)
        self.eventLog.register(WKEvents.WK_EXPORTED, exportHandler)
        self.eventLog.register(WKEvents.WK_IMPORTED, importHandler)
