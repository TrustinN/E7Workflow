from src.app.components.graph.model import GraphModel
from src.app.components.graph.ui import GraphScene
from src.app.state import Context, Selection, SelectionType


class MiniViewController:
    def __init__(self, context: Context, scene: GraphScene, model: GraphModel):
        self.context = context
        self.scene = scene
        self.model = model

        self.activeParent = None
        self.scene.nodeCreated.connect(self.onNodeCreate)
        self.scene.edgeCreated.connect(self.onEdgeCreate)

        self.scene.nodeSelected.connect(self.onNodeSelected)
        self.scene.edgeSelected.connect(self.onEdgeSelected)
        self.scene.rootSelected.connect(self.onRootSelected)

        self.context.selectionModel.selected_.connect(self.onExternalSelection)

        self._updatingSelection = False

    def onNodeCreate(self, id):
        if self.model.parentNode(id) != self.activeParent:
            self.scene.setNodeVisible(id, False)
            return

        self.scene.setNodeVisible(id, True)

    def onEdgeCreate(self, id):
        if self.model.isCrossEdge(id):
            self.scene.setEdgeVisible(id, False)
            return

        if self.model.parentEdge(id) != self.activeParent:
            self.scene.setEdgeVisible(id, False)
            return

        self.scene.setEdgeVisible(id, True)

    def onNodeSelected(self, id):
        self._updatingSelection = True
        self.context.selectionModel.setSelected(id, SelectionType.WORKSPACE)
        self._updatingSelection = False

    def onEdgeSelected(self, id):
        self._updatingSelection = True
        self.context.selectionModel.setSelected(id, SelectionType.EDGE)
        self._updatingSelection = False

    def onRootSelected(self):
        self._updatingSelection = True
        root = self.activeParent
        if not root:
            self.context.selectionModel.setSelected(None, SelectionType.NONE)
        else:
            self.context.selectionModel.setSelected(root, SelectionType.WORKSPACE)
        self._updatingSelection = False

    def renderComponent(self, id):
        self.scene.hideAll()

        if not id:
            return

        for node in self.model.getComponentNodes(self.activeParent):
            self.scene.setNodeVisible(node, True)

        for edge in self.model.getComponentEdges(self.activeParent):
            self.scene.setEdgeVisible(edge, True)

    def onExternalSelection(self, selection: Selection):
        if self._updatingSelection:
            return

        if not selection.id:
            self.activeParent = None
            self.renderComponent(self.activeParent)

        elif selection.type == SelectionType.WORKSPACE:
            self.activeParent = selection.id
            self.renderComponent(self.activeParent)
            self.scene.selectNode(selection.id)

        elif selection.type == SelectionType.EDGE:
            self.activeParent = self.model.parentEdge(selection.id)
            self.renderComponent(self.activeParent)
            self.scene.selectEdge(selection.id)

    def resetState(self):
        self._updatingSelection = False
        self.view.clearState()
