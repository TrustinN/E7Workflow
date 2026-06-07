from PyQt5.QtCore import pyqtSignal

from src.app.frontend.graph.components import GraphScene
from src.app.frontend.graph.widgets import GraphViewWidget
from src.app.frontend.models import GraphModel, TreeModel
from src.app.frontend.state import SelectionModel


class GraphMiniView(GraphViewWidget):
    rootCreated_ = pyqtSignal(str)
    nodeCreated_ = pyqtSignal(str, str)

    nodeUpdated_ = pyqtSignal(str)

    def __init__(
        self,
        model: GraphModel,
        viewModel: TreeModel,
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
        self._updatingSelection = False

        self.rootCreated_.connect(self.viewModelRootCreate)
        self.nodeCreated_.connect(self.viewModelNodeCreate)
        self.nodeUpdated_.connect(self.viewModelNodeUpdate)
        self.viewModel.modelReset_.connect(self.onViewModelReset)

    def onExternalSelection(self, id):
        if self._updatingSelection:
            return

        prevID = self.selectionModel.getPrevSelected()
        if prevID:
            parentID = self.viewModel.parent(prevID)
            if parentID:
                scene = self.scenes[parentID]
                scene.unselectNode(prevID)

        id = id or self.root
        scene = self.scenes.get(id)
        self.setScene(scene)

    def onNodeSelected(self, id):
        if self._updatingSelection:
            return

        self._updatingSelection = True
        prevID = self.selectionModel.getPrevSelected()
        if prevID:
            parentID = self.viewModel.parent(prevID)
            if parentID:
                scene = self.scenes[parentID]
                scene.unselectNode(prevID)
        self.selectionModel.setSelected(id)
        self._updatingSelection = False

    def onNodeDeselected(self, sceneID):
        if self._updatingSelection:
            return

        self.selectionModel.setSelected(sceneID)

    def onNodeCreate(self, nodeID: str):
        nodeData = self.model.getNodeData(nodeID)

        parentID = nodeData["parentID"]
        isRoot = parentID == nodeID
        if isRoot:
            self.createRoot(nodeID)
            return

        self.createGraph(nodeID)
        self.createNode(parentID, nodeID)
        self.updateNode(nodeID, {"displayText": nodeData["text"]})

    def onEdgeCreate(self, edgeIDs: tuple[str, str]):
        pass

    def _createScene(self, id):
        scene = GraphScene()
        scene.nodeSelected_.connect(self.onNodeSelected)
        scene.nodeDeselected_.connect(lambda: self.onNodeDeselected(id))
        scene.nodeMoved_.connect(self.nodeUpdated_)
        return scene

    def createRoot(self, id):
        scene = self.createGraph(id)
        self.setScene(scene)
        self.root = id

        self.rootCreated_.emit(id)

    def createGraph(self, graphID: str):
        scene = self._createScene(graphID)
        self.scenes[graphID] = scene

        return scene

    def createNode(self, graphID: str, nodeID: str):
        parent = self.scenes[graphID]
        parent.createNode(nodeID)

        self.nodeCreated_.emit(nodeID, graphID)

    def createEdge(self, edgeIDs: tuple[str, str]):
        pass

    def updateNode(self, nodeID: str, data):
        parentID = self.viewModel.parent(nodeID)
        parent = self.scenes[parentID]
        parent.updateNode(nodeID, data)

        self.nodeUpdated_.emit(nodeID)

    def viewModelRootCreate(self, nodeID):
        self.viewModel.createRoot(nodeID, {})

    def viewModelNodeCreate(self, nodeID, parentID):
        scene = self.scenes[parentID]
        nodeData = scene.readNode(nodeID)
        self.viewModel.createNode(nodeID, parentID, nodeData)

    def viewModelNodeUpdate(self, nodeID):
        parentID = self.viewModel.parent(nodeID)
        scene = self.scenes[parentID]
        nodeData = scene.readNode(nodeID)
        self.viewModel.updateNode(nodeID, nodeData)

    def onViewModelReset(self):
        for nodeID in self.viewModel.nodeIter():
            if self.viewModel.isRoot(nodeID):
                continue

            data = self.viewModel.nodeData(nodeID)
            self.updateNode(nodeID, data)

    def clearState(self):
        for scene in self.scenes.values():
            scene.deleteLater()

        self.root = None
        self.scenes.clear()
        self.setScene(None)
