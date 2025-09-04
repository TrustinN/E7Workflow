from dataclasses import asdict

from PyQt5.QtCore import QPointF

from .model import EdgeData, GraphData, GraphModel, NodeData
from .view import GraphView


class GraphController:
    def __init__(self, model: GraphModel, view: GraphView):
        self.model = model
        self.view = view

        self.signalOriginView = False

        self.model.nodeCreated_.connect(self.onNodeCreated)
        self.model.edgeCreated_.connect(self.onEdgeCreated)

        self.model.nodeUpdated_.connect(self.onNodeUpdated)
        self.model.edgeUpdated_.connect(self.onEdgeUpdated)

        self.model.dataChanged_.connect(self.onDataChanged)

        self.view.nodePressed_.connect(self.onNodePressed)
        self.view.nodeMoved_.connect(self.onNodeMoved)

    def onNodeCreated(self, id, data: NodeData):
        self.view.createNode(id)
        self.view.updateNode(id, asdict(data))

    def onEdgeCreated(self, id1, id2, data: EdgeData):
        self.view.createEdge(id1, id2)
        self.view.updateEdge(id1, id2, asdict(data))

    def onNodeUpdated(self, id, data: NodeData):
        if self.signalOriginView:
            return
        self.view.updateNode(id, asdict(data))

    def onEdgeUpdated(self, id1, id2, data: EdgeData):
        if self.signalOriginView:
            return
        self.view.updateEdge(id1, id2, asdict(data))

    def onNodePressed(self, id):
        self.signalOriginView = True
        self.model.setSelectedNode(id)
        self.signalOriginView = False

    def onNodeMoved(self, id, pos: QPointF):
        self.signalOriginView = True
        data = NodeData()
        data.pos = pos
        self.model.updateNode(id, data)
        self.signalOriginView = False

    def onDataChanged(self, data: GraphData):
        if self.signalOriginView:
            return

        raise RuntimeError("TODO")

    def createNode(self, id):
        self.model.createNode(id)

    def createEdge(self, id1, id2):
        self.model.createEdge(id1, id2)

    def selectedNode(self):
        return self.model.selectedNode()
