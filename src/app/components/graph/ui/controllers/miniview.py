from src.app.components.graph.model import GraphModel
from src.app.components.graph.ui import GraphScene
from src.app.state import Context, Selection, SelectionType


class GraphMiniViewController:
    def __init__(self, context: Context, scene: GraphScene, model: GraphModel):
        self.context = context
        self.scene = scene
        self.model = model

        self.activeParent = None
        self.scene.edgeCreated.connect(self.onEdgeCreate)
        self.scene.nodeCreated.connect(self.onNodeCreate)

        self.scene.nodeSelected.connect(self.onNodeSelected)
        self.scene.edgeSelected.connect(self.onEdgeSelected)
        self.scene.selectionCleared.connect(self.onSelectionClear)

        self.context.selectionModel.selected_.connect(self.onExternalSelection)

        self._updatingSelection = False

    def onEdgeCreate(self, id):
        if self.model.isCrossEdge(id):
            self.scene.setEdgeVisible(id, False)
            return

        if self.model.parentEdge(id) != self.activeParent:
            self.scene.setEdgeVisible(id, False)
            return

        self.scene.setEdgeVisible(id, True)

    def onNodeCreate(self, id):
        if self.model.parentNode(id) != self.activeParent:
            self.scene.setNodeVisible(id, False)
            return

        self.scene.setNodeVisible(id, True)

    def onNodeSelected(self, id):
        self._updatingSelection = True
        self.context.selectionModel.setSelected(id, SelectionType.WORKSPACE)
        self._updatingSelection = False

    def onEdgeSelected(self, id):
        self._updatingSelection = True
        self.context.selectionModel.setSelected(id, SelectionType.EDGE)
        self._updatingSelection = False

    def onSelectionClear(self):
        self._updatingSelection = True
        self.context.selectionModel.setSelected(None, SelectionType.NONE)
        self._updatingSelection = False

    def renderComponent(self):
        for node in self.model.getComponentNodes(self.activeParent):
            self.scene.setNodeVisible(node, True)

        for edge in self.model.getComponentEdges(self.activeParent):
            self.scene.setEdgeVisible(edge, True)

    def onExternalSelection(self, selection: Selection):
        if self._updatingSelection:
            return

        self.scene.hideAll()

        if not selection.id:
            self.activeParent = None
            return

        if selection.type == SelectionType.WORKSPACE:
            self.activeParent = selection.id
            self.scene.selectNode(selection.id)

        elif selection.type == SelectionType.EDGE:
            schema = self.model.getEdge(selection.id)
            self.activeParent = self.model.getNode(schema.source).parent
            self.scene.selectEdge(selection.id)

        if self.activeParent:
            self.renderComponent()

    def resetState(self):
        self._updatingSelection = False
        self.view.clearState()
