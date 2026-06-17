from src.app.frontend.state.layouts import EdgeItem, GraphLayout, NodeItem
from src.app.frontend.widgets.graph.components import NodeSchema
from src.app.frontend.widgets.graph.views import GraphView


class GraphLayoutSync:
    def __init__(self, layout: GraphLayout, view: GraphView):
        self.layout = layout
        self.view = view

        self.view.nodeCreated_.connect(self.updateNodeLayout)
        self.view.nodeUpdated_.connect(self.updateNodeLayout)
        self.view.edgeCreated_.connect(self.updateEdgeLayout)

        self.freeze = False

    def updateNodeLayout(self, id):
        if self.freeze:
            return

        schema = self.view.readNode(id)
        item = NodeItem(
            position=schema.position,
            color=schema.color,
            borderColor=schema.borderColor,
            geometry=schema.geometry,
            displayText=schema.displayText,
        )

        self.layout.nodes[id] = item

    def updateEdgeLayout(self, id):
        if self.freeze:
            return

        schema = self.view.readEdge(id)
        item = EdgeItem(start=schema.start, end=schema.end)
        self.layout.edges[id] = item

    def freezeLayout(self):
        self.freeze = True

    def unfreezeLayout(self):
        self.freeze = False

    def rerenderView(self):
        for nodeID in self.layout.nodes:
            data = self.layout.nodes[nodeID]
            schema = NodeSchema(
                position=data.position,
                color=data.color,
                borderColor=data.borderColor,
                geometry=data.geometry,
                displayText=data.displayText,
            )
            self.view.updateNode(nodeID, schema)

    def resetState(self):
        self.freeze = False
