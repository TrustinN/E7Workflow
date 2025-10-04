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
        self.eventLog.register(EventType.WORKSPACE_FOCUSED, self.onWorkspaceFocused)

    def getSceneNodePair(self, wksID):
        sceneID = self.workspaceViewMapping.get(wksID)
        nodeID = self.workspaceNodeMapping.get(wksID)
        return sceneID, nodeID

    def setScene(self, sceneID):
        scene = self.scenes[sceneID]
        self.widget.setScene(scene)
        self.activeScene = sceneID

    def onWorkspaceCreated(self, data):
        wksID = data.get("id")

        scene, sceneID = self.controller.createGraph()
        self.scenes[sceneID] = scene
        self.workspaceViewMapping[wksID] = sceneID

        if not self.activeScene:
            self.setScene(sceneID)

        else:
            parentScene = self.widget.scene
            nodeID = self.controller.createNode(parentScene, self.activeScene)
            self.workspaceNodeMapping[wksID] = nodeID

    def onWorkspaceUpdated(self, data):
        wksID = data.get("id")

        _, nodeID = self.getSceneNodePair(wksID)

        nodeData = {"displayText": data.get("text")}

        if nodeID:
            self.controller.updateNode(
                self.scenes[self.activeScene], self.activeScene, nodeID, nodeData
            )

    def onWorkspaceFocused(self, data):
        wksID = data.get("id")
        sceneID, _ = self.getSceneNodePair(wksID)

        if sceneID:
            self.setScene(sceneID)

    def onEdgeCreated(self):
        parentScene = self.widget.scene
        if parentScene:
            self.controller.createEdge(parentScene, self.activeScene)
