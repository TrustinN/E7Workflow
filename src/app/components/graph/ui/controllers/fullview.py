from src.app.components.graph.model import GraphModel, GraphViewState, NodeType
from src.app.components.graph.ui.graphics import GraphScene
from src.app.state import Context, Selection, SelectionType


class FullViewController:
    def __init__(
        self,
        context: Context,
        scene: GraphScene,
        model: GraphModel,
        viewModel: GraphViewState,
    ):
        self.context = context
        self.scene = scene
        self.model = model
        self.viewModel = viewModel

        self.scene.nodeCreated.connect(self.onNodeCreate)

        self.scene.nodeSelected.connect(self.onNodeSelected)
        self.scene.edgeSelected.connect(self.onEdgeSelected)
        self.scene.rootSelected.connect(self.onRootSelected)

        self.context.selectionModel.selected_.connect(self.onExternalSelection)

        self._updatingSelection = False

    def onNodeCreate(self, id):
        schema = self.model.getNode(id)
        self.viewModel.updateNode(
            id,
            {"displayText": schema.group, "shape": NodeType.CIRCLE},
        )

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
        self.context.selectionModel.setSelected(None, SelectionType.NONE)
        self._updatingSelection = False

    def onExternalSelection(self, selection: Selection):
        if self._updatingSelection:
            return

        self.scene.clearSelection()

        if not selection.id:
            return

        if selection.type == SelectionType.WORKSPACE:
            self.scene.selectNode(selection.id)

        elif selection.type == SelectionType.EDGE:
            self.scene.selectEdge(selection.id)
