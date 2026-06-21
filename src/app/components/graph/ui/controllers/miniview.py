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
        if not self.isEdge(id):
            self.scene.setEdgeVisible(id, False)
            return

        schema = self.model.getEdge(id)
        parent = self.model.getNode(schema.source).parent
        if parent != self.activeParent:
            self.scene.setEdgeVisible(id, False)
            return

        self.scene.setEdgeVisible(id, True)

    def onNodeCreate(self, id):
        parent = self.model.getNode(id).parent
        if parent != self.activeParent:
            self.scene.setNodeVisible(id, False)
            return

        self.scene.setNodeVisible(id, True)

    def isEdge(self, id):
        schema = self.model.getEdge(id)
        n1 = self.model.getNode(schema.source)
        n2 = self.model.getNode(schema.target)
        return n1.parent == n2.parent

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

    def showComponent(self):
        schema = self.model.getNode(self.activeParent)
        children = schema.children
        for child in children:
            self.scene.setNodeVisible(child, True)

            for edge in self.model.getNodeEdges(child):
                self.scene.setEdgeVisible(edge, self.isEdge(edge))

    def onExternalSelection(self, selection: Selection):
        if self._updatingSelection:
            return

        self.scene.hideAll()

        prev = self.context.selectionModel.getPrevSelected()
        if prev.id:
            self.scene.clearSelection()

        if not selection.id:
            self.activeParent = None
            self.scene.clearSelection()
            return

        if selection.type == SelectionType.WORKSPACE:
            self.activeParent = selection.id
            self.scene.selectNode(selection.id)

        elif selection.type == SelectionType.EDGE:
            schema = self.model.getEdge(selection.id)
            self.activeParent = self.model.getNode(schema.source).parent
            self.scene.selectEdge(selection.id)

        if self.activeParent:
            self.showComponent()

    def resetState(self):
        self._updatingSelection = False
        self.view.clearState()
