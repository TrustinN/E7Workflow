from src.app.frontend.graph.components import GraphScene
from src.app.frontend.graph.mvc.model import GraphModel
from src.app.frontend.graph.widgets import GraphViewWidget
from src.app.frontend.state import SelectionModel


class GraphFullView(GraphViewWidget):
    def __init__(
        self,
        model: GraphModel,
        viewModel: GraphModel,
        selectionModel: SelectionModel,
    ):
        super().__init__()
        self.model = model
        self.viewModel = viewModel
        self.selectionModel = selectionModel

        self.model.nodeCreated_.connect(self.onNodeCreate)
        self.model.edgeCreated_.connect(self.onEdgeCreate)
        self.selectionModel.selected_.connect(self.onSelectionChanged)

    def onSelectionChanged(self, id):
        if id in self.scene.nodes:
            self.scene.selectNode(id)
        else:
            self.scene.clearSelection()

    def onGraphCreate(self, graphID: str):
        scene = GraphScene()

        if self.scene is None:
            self.setScene(scene)
            self.scene.nodeSelected_.connect(self.selectionModel.setSelected)
            self.scene.nodeDeselected_.connect(
                lambda: self.selectionModel.setSelected(graphID)
            )

    def onNodeCreate(self, nodeID: str):
        nodeData = self.model.getNodeData(nodeID)

        parentID = nodeData["parentID"]
        isRoot = parentID == nodeID
        if isRoot:
            self.onGraphCreate(nodeID)
            return

        self.scene.createNode(nodeID)
        self.scene.updateNode(nodeID, {"displayText": nodeData["text"]})

    def onEdgeCreate(self, edgeIDs: tuple[str, str]):
        pass
