from PyQt5.QtCore import QObject, pyqtSignal
from src.io.io import Serializer

from ..constants import ROOT_ID
from ..graph.editor import InteractiveGraphScene
from ..workspace.helpers import actions
from ..workspace.workspace import WORKSPACE_DEFAULT_COLOR, Workspace, extractGeometry
from .data import WorkspaceData


class WorkspaceManager(QObject):
    workspaceRegistered = pyqtSignal(object)
    activeChanged = pyqtSignal(object)
    sendData_ = pyqtSignal(object)
    dataUpdate = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.activeData = None
        self.activeScene = None

        self.dataHandler: dict[any, WorkspaceData] = {}
        self.sceneHandler: dict[any, InteractiveGraphScene] = {}

    def initState(self):
        rootWks = Workspace(ROOT_ID, "Root")
        rootWks.show()
        rootWks.unlock()
        rootWks.setPadding(15)

        self.registerWorkspace(rootWks)

    def reset(self):
        rootWks = self.workspace(ROOT_ID)
        rootWks.deleteLater()

        self.dataHandler.clear()
        self.sceneHandler.clear()

        self.activeData = None
        self.activeScene = None

        self.initState()

    def registerWorkspace(self, wks: Workspace):
        wks.mousePress.connect(lambda: self.setActiveWorkspace(id))

        id = wks.id
        data = WorkspaceData()
        scene = InteractiveGraphScene()

        data.workspace = wks

        scene.nodeSelected_.connect(
            lambda prevId: self.workspace(prevId).setColor(WORKSPACE_DEFAULT_COLOR)
        )

        self.dataHandler[id] = data
        self.sceneHandler[id] = scene

        if id == ROOT_ID:
            self.setActiveWorkspace(ROOT_ID)

        activeWks = self.workspace()
        if id != ROOT_ID:
            activeWks.addChild(wks)
            self.workspaceRegistered.emit(id)

            data.edges = self.scene().tuples[id]
            self.setAction(id, "none")

    def setActiveWorkspace(self, id):
        self.activeData = self.data(id)
        if self.activeScene:
            self.activeScene.setActiveNode(None)
        self.activeScene = self.scene(id)

        self.activeChanged.emit(id)

    def setAction(self, wksID, action):
        data = self.data(wksID)
        data.action = actions[action]["func"]
        self.dataUpdate.emit()

    def parentID(self, id):
        if id == ROOT_ID:
            return id

        return self.workspace(id).parentID

    def workspace(self, id=None) -> Workspace:
        if id:
            return self.data(id).workspace
        else:
            return self.data().workspace

    def scene(self, id=None) -> InteractiveGraphScene:
        if id:
            return self.sceneHandler[id]
        else:
            return self.activeScene

    def data(self, id=None) -> WorkspaceData:
        if id:
            return self.dataHandler[id]
        else:
            return self.activeData

    def sendData(self, id):
        self.sendData_.emit(self.data(id))

    def getWorkspaceSnapshot(self, workspace: Workspace):
        scene = self.scene(workspace.parentID)
        nodePos = scene.node(workspace.id).pos()
        data = self.data(workspace.id)
        return {
            "edges": data.edges,
            "geometry": extractGeometry(workspace),
            "ID": workspace.id,
            "name": workspace.name,
            "parentID": workspace.parentID,
            "nodeGeometry": [nodePos.x(), nodePos.y()],
            "action": data.action.__name__,
        }

    def snapshot(self, serializer: Serializer):
        snapshots = []

        def getData(workspace: Workspace):
            for wks in workspace.wkspaces:
                snapshots.append(self.getWorkspaceSnapshot(wks))
                getData(wks)

        rootWks = self.workspace(ROOT_ID)
        getData(rootWks)

        for data in snapshots:
            serializer.addLog("restoreWorkspace", data)

        for data in snapshots:
            serializer.addLog("restoreEdges", data)

        for data in snapshots:
            serializer.addLog("restoreActions", data)
