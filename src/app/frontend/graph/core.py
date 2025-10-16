from src.app.frontend.components import Component
from src.app.frontend.context import ContextManager
from src.app.frontend.events import EventHandler, EventLog, inject
from src.router.routing import Dispatcher

from .components import (
    GraphRepository,
    GraphSerializer,
    GraphSerializerComponent,
    GraphUI,
    GraphUIComponent,
)
from .context import GraphContextManager
from .widget import GraphWidget


class GraphComponent(Component):
    CREATE_ROOT = "Create Root Scene"
    CREATE_SCENE = "Create Scene and Node"
    UPDATE_NODE = "Update Node"
    ON_FOCUS = "On Focus"
    IMPORT = "Import"
    EXPORT = "Export"

    def __init__(
        self,
        ctxManager: ContextManager,
        eventLog: EventLog,
        dispatcher: Dispatcher,
    ):
        super().__init__()
        self.ctxManager = GraphContextManager(ctxManager)
        self.widget = GraphWidget()
        self.eventLog = eventLog

        self.repository = GraphRepository(dispatcher)

        self.graphUI = GraphUI(self.widget, self.repository)
        self.guiCpt = GraphUIComponent(self.graphUI)

        self.serializer = GraphSerializer(self.graphUI)
        self.serialCpt = GraphSerializerComponent(self.serializer)

        capabilities = self._getCapabilities()
        handlers = self._createHandlers(capabilities)
        for name, capability in handlers.items():
            self.registerCapability(name, capability)

    def _createHandlers(self, capabilities):
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
            self.CREATE_ROOT: createRootHandler,
            self.CREATE_SCENE: createdHandler,
            self.UPDATE_NODE: updatedHandler,
            self.ON_FOCUS: focusedHandler,
            self.IMPORT: importHandler,
            self.EXPORT: exportHandler,
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
