from src.app.frontend.widgets.graph.components import (
    EdgeSchema,
    GraphScene,
    NodeSchema,
    NodeType,
)

from .view import GraphView


class GraphMultiView(GraphView):

    def __init__(self):
        super().__init__()

        self.scenes: dict[str, GraphScene] = {}
        self.nodeParents: dict[str, str] = {}
        self.edgeParents: dict[str, str] = {}

    def selectNode(self, nodeID: str, parentID: str):
        scene = self.scenes[parentID]
        scene.selectNode(nodeID)

    def unselectNode(self, nodeID: str, parentID: str):
        scene = self.scenes[parentID]
        scene.unselectNode(nodeID)

    def clearSelection(self, id):
        scene = self.scenes[id]
        scene.clearSelection()

    def switchScene(self, id):
        scene = self.scenes.get(id)
        self.setScene(scene)

    def _createScene(self, id):
        scene = GraphScene()
        scene.nodeSelected_.connect(self.nodeSelected_.emit)
        scene.nodeDeselected_.connect(self.nodeDeselected_.emit)
        scene.nodeMoved_.connect(self.nodeUpdated_.emit)
        scene.edgeMoved_.connect(self.edgeUpdated_.emit)
        return scene

    def createGraph(self, graphID: str):
        scene = self._createScene(graphID)
        self.scenes[graphID] = scene

    def createNode(self, nodeID: str, graphID: str, nodeType=NodeType.RECTANGLE):
        parent = self.scenes[graphID]
        parent.createNode(nodeID, nodeType)

        self.nodeParents[nodeID] = graphID
        self.nodeCreated_.emit(nodeID)

    def createEdge(self, edgeID: str, e1: str, e2: str, graphID: str):
        parent = self.scenes[graphID]
        parent.createEdge(edgeID, e1, e2)

        self.edgeParents[edgeID] = graphID
        self.edgeCreated_.emit(edgeID)

    def updateNode(self, nodeID: str, data: NodeSchema):
        parentID = self.nodeParents[nodeID]
        scene = self.scenes[parentID]
        scene.updateNode(nodeID, data)

        self.nodeUpdated_.emit(nodeID)

    def readNode(self, nodeID: str) -> NodeSchema:
        parentID = self.nodeParents[nodeID]
        scene = self.scenes[parentID]
        data = scene.readNode(nodeID)
        return data

    def readEdge(self, edgeID: str) -> EdgeSchema:
        parentID = self.edgeParents[edgeID]
        scene = self.scenes[parentID]
        data = scene.readEdge(edgeID)
        return data

    def clearState(self):
        for scene in self.scenes.values():
            scene.deleteLater()

        self.scenes.clear()
        self.nodeParents.clear()
        self.edgeParents.clear()
        self.setScene(None)
