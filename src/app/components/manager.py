from PyQt5.QtCore import QObject, pyqtSignal
from src.io.io import Serializer

from ..constants import ROOT_ID
from ..graph.editor import InteractiveGraphScene
from ..workspace.helpers import click, screenshot, scroll
from ..workspace.workspace import Workspace, extractGeometry

actions = [
    {
        "name": click.__name__,
        "desc": "Clicks the center of the workspace",
        "action": click,
    },
    {
        "name": screenshot.__name__,
        "desc": "Takes a screenshot given the borders of the workspace",
        "action": screenshot,
    },
    {
        "name": scroll.__name__,
        "action": scroll,
        "desc": "Drags the mouse from one edge to the opposite edge given a scroll direction",
    },
]


class WorkspaceData:
    def __init__(self):
        self.action = None
        self.edges = None


class WorkspaceManager(QObject):
    workspaceRegistered = pyqtSignal(object)
    activeChanged = pyqtSignal(object)

    def __init__(self):
        super().__init__()
        self.activeWks = None
        self.activeScene = None
        self.wksHandler: dict[any, Workspace] = {}
        self.sceneHandler: dict[any, InteractiveGraphScene] = {}

    def initState(self):
        self.wksHandler[ROOT_ID] = Workspace(ROOT_ID, "Root")

        rootWks = self.workspace(ROOT_ID)
        rootWks.show()
        rootWks.unlock()
        rootWks.setPadding(15)

        self.registerWorkspace(rootWks)
        self.setActiveWorkspace(ROOT_ID)

    def reset(self):
        rootWks = self.workspace(ROOT_ID)
        rootWks.deleteLater()

        self.wksHandler.clear()
        self.sceneHandler.clear()

        self.activeWks = None
        self.activeScene = None

        self.initState()

    def registerWorkspace(self, wks: Workspace):
        id = wks.id
        if self.activeWks:
            self.activeWks.addChild(wks)

        self.wksHandler[id] = wks
        self.sceneHandler[id] = InteractiveGraphScene()

        wks.mousePress.connect(lambda: self.setActiveWorkspace(id))

        if id != ROOT_ID:
            self.workspaceRegistered.emit(id)

    def setActiveWorkspace(self, id):
        self.activeWks = self.workspace(id)
        self.activeScene = self.scene(id)

        self.activeChanged.emit(id)

    def parentID(self, id):
        if id == ROOT_ID:
            return id

        return self.workspace(id).parentID

    def workspace(self, id) -> Workspace:
        return self.wksHandler[id]

    def scene(self, id) -> InteractiveGraphScene:
        return self.sceneHandler[id]

    def getWorkspaceSnapshot(self, workspace: Workspace):
        scene = self.scene(workspace.parentID)
        nodePos = scene.node(workspace.id).pos()
        return {
            "edges": scene.tuples[workspace.id],
            "geometry": extractGeometry(workspace),
            "ID": workspace.id,
            "name": workspace.name,
            "parentID": workspace.parentID,
            "nodeGeometry": [nodePos.x(), nodePos.y()],
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
