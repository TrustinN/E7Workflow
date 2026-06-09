from PyQt5.QtCore import pyqtSignal

from src.app.frontend.widgets.graph.components import GraphScene, NodeType

from .view import GraphView


class GraphMultiView(GraphView):
    nodeCreated_ = pyqtSignal(str, str)
    edgeCreated_ = pyqtSignal(str, str)

    nodeUpdated_ = pyqtSignal(str)
    edgeUpdated_ = pyqtSignal(str, str)

    nodeSelected_ = pyqtSignal(str)
    nodeDeselected_ = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.scenes: dict[str, GraphScene] = {}

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

    def createNode(self, graphID: str, nodeID: str, nodeType=NodeType.RECTANGLE):
        parent = self.scenes[graphID]
        parent.createNode(nodeID, nodeType)

        self.nodeCreated_.emit(nodeID, graphID)

    def createEdge(self, graphID: str, e1: str, e2: str):
        parent = self.scenes[graphID]
        parent.createEdge(e1, e2)

        self.edgeCreated_.emit(e1, e2)

    def updateNode(self, nodeID: str, parentID: str, data):
        scene = self.scenes[parentID]
        scene.updateNode(nodeID, data)

        self.nodeUpdated_.emit(nodeID)

    def updateEdge(self, e1: str, e2: str, parentID: str, data):
        scene = self.scenes[parentID]
        scene.updateEdge(e1, e2, data)

        self.edgeUpdated_.emit(e1, e2)

    def readNode(self, nodeID: str, parentID: str):
        scene = self.scenes[parentID]
        data = scene.readNode(nodeID)
        return data

    def readEdge(self, e1: str, e2: str, parentID: str):
        scene = self.scenes[parentID]
        data = scene.readEdge(e1, e2)
        return data

    def clearState(self):
        for scene in self.scenes.values():
            scene.deleteLater()

        self.scenes.clear()
        self.setScene(None)
