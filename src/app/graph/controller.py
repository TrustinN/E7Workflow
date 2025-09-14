from src.router.routing import Client, Dispatcher, Link

from ..event.events import EventLog, EventType
from .service import gs
from .widget import GraphWidget


class GraphController:
    def __init__(self, eventLog: EventLog, dispatcher: Dispatcher, widget: GraphWidget):
        self.widget = widget
        self.client = Client("Graph Controller", dispatcher)
        self.eventLog = eventLog

        self.eventLog.register(EventType.WORKSPACE_CREATED, self.onWorkspaceCreated)
        self.eventLog.register(EventType.WORKSPACE_FOCUSED, self.onWorkspaceFocused)

        self.sceneWksMappings = {}
        self.nodeWksMappings = {}

        self.wksSceneMappings = {}
        self.wksNodeMappings = {}

        self.nodeStart = None

        response = self.createGraph()
        self.widget.setActiveGraph(response["graphID"])

    def onWorkspaceCreated(self, data):
        wsID = data["id"]

        response = self.createGraph()
        graphID = response["graphID"]
        self.sceneWksMappings[graphID] = wsID
        self.wksSceneMappings[wsID] = graphID

        response = self.createNode()
        nodeID = response["nodeID"]
        self.nodeWksMappings[nodeID] = wsID
        self.wksNodeMappings[wsID] = nodeID

    def onWorkspaceFocused(self, data):
        wsID = data["id"]
        graphID = self.wksSceneMappings[wsID]
        self.widget.setActiveGraph(graphID)

    def createGraph(self):
        link = Link(gs.NAME, gs.GRAPH)
        response = self.client.post(link)
        graphID = response["graphID"]
        self.widget.createGraph(graphID)

        return response

    def createNode(self):
        link = Link(gs.NAME, gs.GRAPH, self.widget.activeGraph, gs.NODE)
        response = self.client.post(link)
        nodeID = response["nodeID"]
        self.widget.createNode(nodeID)

        return response

    def createEdge(self):
        id1 = self.nodeStart
        id2 = self.widget.scene.selectedNode()
        if not id2:
            return

        if not id1:
            self.nodeStart = id2
            return

        link = Link(gs.NAME, gs.GRAPH, self.widget.activeGraph, gs.EDGE)
        self.client.post(link, {"nodeID1": id1, "nodeID2": id2})
        self.nodeStart = None
        self.widget.createEdge(id1, id2)
