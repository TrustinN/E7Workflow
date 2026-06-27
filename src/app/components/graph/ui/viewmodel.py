from src.app.components.graph.model import (
    EdgeViewState,
    GraphModel,
    GraphViewState,
    NodeViewState,
)

from .scene import GraphScene


class GraphViewModel:
    def __init__(self, scene: GraphScene, model: GraphModel, viewState: GraphViewState):
        self.scene = scene
        self.model = model
        self.viewState = viewState

        self.model.nodeCreated.connect(self.onNodeCreated)
        self.model.nodeDeleted.connect(self.onNodeDeleted)

        self.model.edgeCreated.connect(self.onEdgeCreated)
        self.model.edgeDeleted.connect(self.onEdgeDeleted)

        self.model.modelCleared.connect(self.onModelCleared)

        self.viewState.nodeUpdated.connect(self.onNodeStateChanged)
        self.viewState.edgeUpdated.connect(self.onEdgeStateChanged)
        self.viewState.modelLoaded.connect(self.rebuild)

        self.scene.nodeUpdated.connect(self.onSceneNodeChanged)
        self.scene.edgeUpdated.connect(self.onSceneEdgeChanged)

    def onNodeCreated(self, id):
        state = NodeViewState()
        self.viewState.addNode(id, state)
        self.scene.createNode(id, state.toData())

    def onEdgeCreated(self, id):
        edge = self.model.getEdge(id)
        state = EdgeViewState()
        self.viewState.addEdge(id, state)
        self.scene.createEdge(
            id,
            edge.source,
            edge.target,
            state.toData(),
        )

    def onNodeDeleted(self, id):
        self.viewState.deleteNode(id)
        self.scene.deleteNode(id)

    def onEdgeDeleted(self, id):
        self.viewState.deleteEdge(id)
        self.scene.deleteEdge(id)

    def onModelCleared(self):
        self.viewState.clear()
        self.scene.clear()

    def onNodeStateChanged(self, id):
        state = self.viewState.getNode(id)
        self.scene.updateNode(id, state.toData())

    def onEdgeStateChanged(self, id):
        state = self.viewState.getEdge(id)
        self.scene.updateEdge(id, state.toData())

    def onSceneNodeChanged(self, id):
        data = self.scene.readNode(id)
        self.viewState.updateNode(id, data)

    def onSceneEdgeChanged(self, id):
        data = self.scene.readEdge(id)
        self.viewState.updateEdge(id, data)

    def rebuild(self):
        for id in self.model.nodeList():
            state = self.viewState.getNode(id)
            self.scene._createNode(id, state.toData())

        for id in self.model.edgeList():
            edge = self.model.getEdge(id)
            state = self.viewState.getEdge(id)
            self.scene._createEdge(id, edge.source, edge.target, state.toData())
