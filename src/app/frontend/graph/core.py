from src.app.frontend.context import Context
from src.app.frontend.events import EventLog, injectData
from src.app.frontend.workspace.events import WKEvents
from src.router.routing import Dispatcher

from .components import (
    GraphRepository,
    GraphSerializer,
    GraphSerializerComponent,
    GraphUI,
    GraphUIComponent,
)
from .widget import GraphWidget


class ContextManager:
    def __init__(self, context: Context):
        self.context = context
        self.context.add("activeScene", None)
        self.context.add("activeNode", None)
        self.context.add("sceneParents", {})
        self.context.add("workspaceViewMapping", {})
        self.context.add("workspaceNodeMapping", {})

    def getData(self):
        return self.context.toDict()

    def updateActiveScene(self, data):
        sceneID = data.get("sceneID")
        self.context.put("activeScene", sceneID)

    def updateSceneParents(self, data):
        sceneID = data.get("sceneID")

        activeID = self.context.get("activeScene")
        if activeID:
            self.context.get("sceneParents")[sceneID] = activeID

    def updateSceneBinding(self, data):
        wksID = data.get("id")
        sceneID = data.get("sceneID")

        self.context.get("workspaceViewMapping")[wksID] = sceneID

    def updateNodeBinding(self, data):
        wksID = data.get("id")
        nodeID = data.get("nodeID")

        self.context.get("workspaceNodeMapping")[wksID] = nodeID


class GraphCore:
    def __init__(
        self,
        widget: GraphWidget,
        context: Context,
        eventLog: EventLog,
        dispatcher: Dispatcher,
    ):
        self.widget = widget

        self.ctxManager = ContextManager(context)

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

        createRootHandler = injectData(self.ctxManager.getData)
        createRootHandler.chain(createGraphUI)
        createRootHandler.chain(self.ctxManager.updateSceneBinding)
        createRootHandler.chain(self.ctxManager.updateActiveScene)

        createdHandler = injectData(self.ctxManager.getData)
        createdHandler.chain(createGraphUI)
        createdHandler.chain(self.ctxManager.updateSceneBinding)
        createdHandler.chain(createNodeUI)
        createdHandler.chain(self.ctxManager.updateNodeBinding)
        createdHandler.chain(self.ctxManager.updateSceneParents)

        updatedHandler = injectData(self.ctxManager.getData)
        updatedHandler.chain(updateNodeUI)

        focusedHandler = injectData(self.ctxManager.getData)
        focusedHandler.chain(setSceneUI)
        # importHandler = EventHandler(serialImport, data=False)
        # exportHandler = EventHandler(serialExport, data=False)

        self.eventLog.register(WKEvents.WK_CREATED_ROOT, createRootHandler)
        self.eventLog.register(WKEvents.WK_CREATED, createdHandler)
        self.eventLog.register(WKEvents.WK_UPDATED, updatedHandler)
        self.eventLog.register(WKEvents.WK_FOCUSED, focusedHandler)
        # self.eventLog.register(WKEvents.WK_EXPORTED, exportHandler)
        # self.eventLog.register(WKEvents.WK_IMPORTED, importHandler)
