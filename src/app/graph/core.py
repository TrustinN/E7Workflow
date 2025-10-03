from ..event.events import EventLog, EventType
from .controller import GraphController
from .widget import GraphWidget


class GraphCore:
    def __init__(
        self,
        widget: GraphWidget,
        controller: GraphController,
        eventLog: EventLog,
    ):
        self.widget = widget
        self.controller = controller

        self.widget.createEdgeBtn.clicked.connect(self.onEdgeCreated)

        self.scenes = {}
        self.activeScene = None
        self.workspaceViewMapping = {}
        self.workspaceNodeMapping = {}

        self.eventLog = eventLog
        self.eventLog.register(
            EventType.WORKSPACE_CREATED,
            self.onWorkspaceCreated,
        )
        self.eventLog.register(EventType.WORKSPACE_UPDATED, self.onWorkspaceUpdated)

    def onWorkspaceCreated(self, data):
        wksID = data.get("id")

        scene, sceneID = self.controller.createGraph()
        self.scenes[sceneID] = scene
        self.workspaceViewMapping[wksID] = sceneID

        if not self.activeScene:
            self.widget.setScene(scene)
            self.activeScene = sceneID

        else:
            parentScene = self.widget.scene
            nodeID = self.controller.createNode(parentScene, self.activeScene)
            self.workspaceNodeMapping[wksID] = nodeID

    def onWorkspaceUpdated(self, data):
        wksID = data.get("id")

        # scene = self.workspaceViewMapping[wksID]
        node = self.workspaceNodeMapping.get(wksID)

        nodeData = {"displayText": data.get("text")}

        if node:
            self.controller.updateNode(
                self.scenes[self.activeScene], self.activeScene, node, nodeData
            )

    def onEdgeCreated(self):
        parentScene = self.widget.scene
        if parentScene:
            self.controller.createEdge(parentScene, self.activeScene)
