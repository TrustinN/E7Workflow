from src.router.routing import Client, Dispatcher, Link

from ..event.events import EventLog, EventType
from .modelView import GraphController
from .service import gs
from .widget import GraphWidget


class GraphRepository:
    def __init__(self, dispatcher: Dispatcher):
        self.client = Client("Graph Repository", dispatcher)

    def createGraph(self):
        link = Link(gs.NAME, gs.GRAPH)
        response = self.client.post(link)
        sceneID = response["graphID"]

        return sceneID

    def createNode(self, graphID):
        link = Link(gs.NAME, gs.GRAPH, graphID, gs.NODE)
        response = self.client.post(link)

        nodeID = response["nodeID"]
        return nodeID

    def updateNode(self, graphID, nodeID, data):
        link = Link(gs.NAME, gs.GRAPH, graphID, gs.NODE, nodeID)
        self.client.put(link, data)

    def createEdge(self, graphID, id1, id2):
        link = Link(gs.NAME, gs.GRAPH, graphID, gs.EDGE)
        self.client.post(link, {"nodeID1": id1, "nodeID2": id2})

    def getGraph(self):
        link = Link(gs.NAME, gs.GRAPH)
        return self.client.get(link)

    def exportGraph(self):
        link = Link(gs.NAME, gs.GRAPH, gs.EXPORT)
        self.client.post(link)

    def importGraph(self):
        link = Link(gs.NAME, gs.GRAPH, gs.IMPORT)
        self.client.post(link)


class GraphContext:
    def __init__(self):
        self.activeScene = None
        self.sceneParents = {}
        self.workspaceViewMapping = {}
        self.workspaceNodeMapping = {}

    def setActive(self, sceneID):
        self.activeScene = sceneID

    @property
    def active(self):
        return self.activeScene

    def parentScene(self, id):
        return self.sceneParents[id]

    def newWorkspace(self, wksID, viewID, nodeID=None):
        self.workspaceViewMapping[wksID] = viewID
        if self.activeScene:
            self.sceneParents[viewID] = self.activeScene
            self.workspaceNodeMapping[wksID] = nodeID

    def sceneNode(self, wksID):
        sceneID = self.workspaceViewMapping.get(wksID)
        nodeID = self.workspaceNodeMapping.get(wksID)
        return sceneID, nodeID


class GraphSerializer:
    def __init__(
        self,
        controller: GraphController,
        repository: GraphRepository,
        context: GraphContext,
    ):
        self.controller = controller
        self.repository = repository

    def export(self):
        graphs = self.repository.getGraph()

        for graphID, graphData in graphs.items():
            nodes = graphData.get("nodes")
            edges = graphData.get("edges")
            graphConfig = graphData.get("data")

            for nodeID in nodes:
                nodeData = self.controller.readNode(graphID, nodeID)
                self.repository.updateNode(graphID, nodeID, nodeData)

        self.repository.exportGraph()

    def restore(self):
        self.controller.clearState()
        self.repository.importGraph()

        graphs = self.repository.getGraph()

        for graphID, graphData in graphs.items():
            nodes = graphData.get("nodes")
            edges = graphData.get("edges")
            graphConfig = graphData.get("data")
            self.controller.createGraph(graphID)

            for nodeID, nodeData in nodes.items():
                self.controller.createNode(graphID, nodeID)
                self.controller.updateNode(graphID, nodeID, nodeData)


class GraphBuilder:
    def __init__(
        self,
        controller: GraphController,
        repository: GraphRepository,
        eventLog: EventLog,
    ):
        self.repository = repository
        self.eventLog = eventLog
        self.controller = controller

    def createGraph(self):
        sceneID = self.repository.createGraph()
        scene = self.controller.createGraph(sceneID)
        return sceneID, scene

    def createNode(self, graphID):
        nodeID = self.repository.createNode(graphID)
        self.controller.createNode(graphID, nodeID)
        return nodeID

    def updateNode(self, graphID, nodeID, data):
        self.controller.updateNode(graphID, nodeID, data)

    def createEdge(self, graphID):
        ids = self.controller.createEdge(graphID)
        if ids:
            self.repository.createEdge(graphID, *ids)


class GraphCore:
    def __init__(
        self,
        widget: GraphWidget,
        controller: GraphController,
        eventLog: EventLog,
        dispatcher: Dispatcher,
    ):
        self.widget = widget
        self.controller = controller

        self.widget.createEdgeBtn.clicked.connect(self.onEdgeCreated)

        self.context = GraphContext()
        self.repository = GraphRepository(dispatcher)
        self.builder = GraphBuilder(controller, self.repository, eventLog)
        self.serializer = GraphSerializer(controller, self.repository, self.context)

        self.eventLog = eventLog
        self.eventLog.register(
            EventType.WORKSPACE_CREATED,
            self.onWorkspaceCreated,
        )
        self.eventLog.register(EventType.WORKSPACE_UPDATED, self.onWorkspaceUpdated)
        self.eventLog.register(EventType.WORKSPACE_FOCUSED, self.onWorkspaceFocused)
        self.eventLog.register(
            EventType.WORKSPACE_EXPORTED, lambda x: self.serializer.export()
        )
        self.eventLog.register(
            EventType.WORKSPACE_IMPORTED, lambda x: self.serializer.restore()
        )

    def setScene(self, sceneID):
        scene = self.controller.scene(sceneID)
        self.widget.setScene(scene)
        self.context.setActive(sceneID)

    def onWorkspaceCreated(self, data):
        wksID = data.get("id")
        sceneID, scene = self.builder.createGraph()
        nodeID = None
        activeID = self.context.active
        if not activeID:
            self.setScene(sceneID)

        else:
            nodeID = self.builder.createNode(activeID)

        self.context.newWorkspace(wksID, sceneID, nodeID)

    def onWorkspaceUpdated(self, data):
        wksID = data.get("id")
        text = data.get("text")

        sceneID, nodeID = self.context.sceneNode(wksID)

        nodeData = {"displayText": text}

        if nodeID:
            parentScene = self.context.parentScene(sceneID)
            self.builder.updateNode(parentScene, nodeID, nodeData)

    def onWorkspaceFocused(self, data):
        wksID = data.get("id")
        sceneID, _ = self.context.sceneNode(wksID)

        if sceneID:
            self.setScene(sceneID)

    def onEdgeCreated(self):
        activeID = self.context.active
        if activeID:
            self.builder.createEdge(activeID)
