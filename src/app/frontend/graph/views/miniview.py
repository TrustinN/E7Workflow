from PyQt5.QtCore import pyqtSignal

from src.app.frontend.graph.components import GraphScene
from src.app.frontend.graph.widgets import GraphViewWidget
from src.app.frontend.models import GraphModel
from src.app.frontend.state import SelectionModel


class GraphMiniView(GraphViewWidget):
    nodeCreated_ = pyqtSignal(str)

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
        self.model.modelClear_.connect(self.clearState)

        self.selectionModel.selected_.connect(self.onExternalSelection)

        self.nodeCreated_.connect(self.viewModelNodeCreate)
        self.viewModel.modelReset_.connect(self.onViewModelReset)

    def onExternalSelection(self, id):
        id = id or self.root
        scene = self.scenes.get(id)
        self.setScene(scene)

    def onNodeSelected(self, id):
        self.selectionModel.selected_.disconnect(self.onExternalSelection)
        self.selectionModel.setSelected(id)
        self.selectionModel.selected_.connect(self.onExternalSelection)

    def onNodeDeselected(self, sceneID):
        self.selectionModel.setSelected(sceneID)

    def onNodeMoved(self, id):
        self.viewModelNodeUpdate(id)

    def _createScene(self, id):
        scene = GraphScene()
        scene.nodeSelected_.connect(self.onNodeSelected)
        scene.nodeDeselected_.connect(lambda: self.onNodeDeselected(id))
        scene.nodeMoved_.connect(self.onNodeMoved)
        return scene

    def onGraphCreate(self, graphID: str):
        scene = self._createScene(graphID)
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

        self.nodeCreated_.emit(nodeID)

    def onEdgeCreate(self, edgeIDs: tuple[str, str]):
        pass

    def viewModelNodeCreate(self, nodeID):
        nodeData = self.scene.readNode(nodeID)
        self.viewModel.createNode(nodeID, nodeData)

    def viewModelNodeUpdate(self, nodeID):
        nodeData = self.scene.readNode(nodeID)
        self.viewModel.updateNode(nodeID, nodeData)

    def onViewModelReset(self):
        for nodeID in self.viewModel.nodeIter():
            renderData = self.viewModel.getNodeData(nodeID)
            nodeData = self.model.getNodeData(nodeID)
            parentID = nodeData["parentID"]
            isRoot = parentID == nodeID
            if isRoot:
                continue

            scene = self.scenes[parentID]
            scene.updateNode(nodeID, renderData)

    def clearState(self):
        for scene in self.scenes.values():
            scene.deleteLater()

        self.root = None
        self.scenes.clear()
        self.setScene(None)
