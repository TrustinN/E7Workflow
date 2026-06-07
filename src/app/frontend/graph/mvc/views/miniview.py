from src.app.frontend.graph.components import GraphScene
from src.app.frontend.graph.mvc.model import GraphModel
from src.app.frontend.graph.widgets import GraphViewWidget
from src.app.frontend.state import SelectionModel


class GraphMiniView(GraphViewWidget):
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

        self.scenes: dict[str, GraphScene] = {}
        self.root = None

        self.model.nodeCreated_.connect(self.onNodeCreate)
        self.model.edgeCreated_.connect(self.onEdgeCreate)

        self.selectionModel.selected_.connect(self.onObjectSelection)

    def onObjectSelection(self, id):
        id = id or self.root
        scene = self.scenes.get(id)
        self.setScene(scene)

    def onGraphCreate(self, graphID: str):
        scene = GraphScene()
        self.scenes[graphID] = scene

        if self.scene is None:
            self.setScene(scene)
            self.root = graphID

    def onNodeCreate(self, nodeID: str):
        nodeData = self.model.getNodeData(nodeID)

        parentID = nodeData["parentID"]
        isRoot = parentID == nodeID
        if isRoot:
            self.onGraphCreate(nodeID)
            return

        self.onGraphCreate(nodeID)
        parent = self.scenes[parentID]
        parent.createNode(nodeID)
        parent.updateNode(nodeID, {"displayText": nodeData["text"]})

    def onEdgeCreate(self, edgeIDs: tuple[str, str]):
        pass
