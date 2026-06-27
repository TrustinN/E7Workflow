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

        self.model.nodeCreated.connect(self.createModelNode)
        self.model.nodeCreated.connect(self.createNode)
        self.model.edgeCreated.connect(self.createModelEdge)
        self.model.edgeCreated.connect(self.createEdge)
        self.model.nodeDeleted.connect(self.deleteModelNode)
        self.model.nodeDeleted.connect(self.deleteNode)
        self.model.edgeDeleted.connect(self.deleteModelEdge)
        self.model.edgeDeleted.connect(self.deleteEdge)
        self.model.modelCleared.connect(self.viewState.clear)
        self.model.modelCleared.connect(self.scene.clear)
        self.model.modelLoaded.connect(self.rebuild)

        self.viewState.nodeUpdated.connect(self.updateNode)
        self.viewState.edgeUpdated.connect(self.updateEdge)
        self.viewState.modelLoaded.connect(self.rerender)

        self.scene.nodeUpdated.connect(self.updateModelNode)
        self.scene.edgeUpdated.connect(self.updateModelEdge)

        self._loading = False

    def createModelNode(self, id):
        state = NodeViewState()
        self.viewState.addNode(id, state)

    def createModelEdge(self, id):
        state = EdgeViewState()
        self.viewState.addEdge(id, state)

    def deleteModelNode(self, id):
        self.viewState.deleteNode(id)

    def deleteModelEdge(self, id):
        self.viewState.deleteEdge(id)

    def createNode(self, id):
        schema = self.viewState.getNode(id)
        self.scene.createNode(id, schema.toData())

    def createEdge(self, id):
        edge = self.model.getEdge(id)
        source = edge.source
        target = edge.target
        schema = self.viewState.getEdge(id)

        self.scene.createEdge(id, source, target, schema.toData())

    def updateNode(self, id):
        state = self.viewState.getNode(id)
        self.scene.updateNode(id, state.toData())

    def updateEdge(self, id):
        state = self.viewState.getEdge(id)
        self.scene.updateEdge(id, state.toData())

    def deleteNode(self, id):
        self.scene.deleteNode(id)

    def deleteEdge(self, id):
        self.scene.deleteEdge(id)

    def updateModelNode(self, id):
        if self._loading:
            return

        data = self.scene.readNode(id)
        self.viewState.updateNode(id, data)

    def updateModelEdge(self, id):
        if self._loading:
            return

        data = self.scene.readEdge(id)
        self.viewState.updateEdge(id, data)

    def rebuild(self):
        self._loading = True
        for id in self.model.nodeList():
            self.scene._createNode(id, {})

        for id in self.model.edgeList():
            schema = self.model.getEdge(id)
            self.scene._createEdge(id, schema.source, schema.target, {})
        self._loading = False

    def rerender(self):
        self._loading = True
        for id in self.model.nodeList():
            schema = self.viewState.getNode(id)
            self.scene.updateNode(id, schema.toData())

        for id in self.model.edgeList():
            schema = self.viewState.getEdge(id)
            self.scene.updateEdge(id, schema.toData())
        self._loading = False
