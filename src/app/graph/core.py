from src.router.routing import Client, Dispatcher, Link

from ..event.events import EventLog, EventType
from .controller import GraphController
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

    def createEdge(self, graphID, id1, id2):
        link = Link(gs.NAME, gs.GRAPH, graphID, gs.EDGE)
        self.client.post(link, {"nodeID1": id1, "nodeID2": id2})


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

        self.repository = GraphRepository(dispatcher)
        self.builder = GraphBuilder(controller, self.repository, eventLog)

        self.activeScene = None
        self.sceneParents = {}
        self.workspaceViewMapping = {}
        self.workspaceNodeMapping = {}

        self.eventLog = eventLog
        self.eventLog.register(
            EventType.WORKSPACE_CREATED,
            self.onWorkspaceCreated,
        )
        self.eventLog.register(EventType.WORKSPACE_UPDATED, self.onWorkspaceUpdated)
        self.eventLog.register(EventType.WORKSPACE_FOCUSED, self.onWorkspaceFocused)

    def getSceneNodePair(self, wksID):
        sceneID = self.workspaceViewMapping.get(wksID)
        nodeID = self.workspaceNodeMapping.get(wksID)
        return sceneID, nodeID

    def setScene(self, sceneID):
        scene = self.controller.scene(sceneID)
        self.widget.setScene(scene)
        self.activeScene = sceneID

    def onWorkspaceCreated(self, data):
        wksID = data.get("id")

        sceneID, scene = self.builder.createGraph()
        self.workspaceViewMapping[wksID] = sceneID

        if not self.activeScene:
            self.setScene(sceneID)

        else:
            self.sceneParents[sceneID] = self.activeScene
            nodeID = self.builder.createNode(self.activeScene)
            self.workspaceNodeMapping[wksID] = nodeID

    def onWorkspaceUpdated(self, data):
        wksID = data.get("id")
        text = data.get("text")

        sceneID, nodeID = self.getSceneNodePair(wksID)

        nodeData = {"displayText": text}

        if nodeID:
            self.builder.updateNode(self.sceneParents[sceneID], nodeID, nodeData)

    def onWorkspaceFocused(self, data):
        wksID = data.get("id")
        sceneID, _ = self.getSceneNodePair(wksID)

        if sceneID:
            self.setScene(sceneID)

    def onEdgeCreated(self):
        if self.activeScene:
            self.builder.createEdge(self.activeScene)
