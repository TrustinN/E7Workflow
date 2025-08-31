from src.io.io import Serializer

from ..workspace.workspace import layoutToBBox
from .data import WorkspaceData
from .state import RunnerState


class AppState:
    def __init__(self, managerState: WorkspaceData, runnerState: RunnerState):
        self.managerState = managerState
        self.runnerState = runnerState

    def serialize(self):
        return {
            "managerState": self.managerState.serialize(),
            "runnerState": self.runnerState.serialize(),
        }


def restoreWorkspace(app, **kwargs):
    geometry = kwargs["geometry"]
    id = kwargs["ID"]
    name = kwargs["name"]
    parentID = kwargs["parentID"]
    padding = kwargs["padding"]
    nodeGeometry = kwargs.get("nodeGeometry")
    childData = kwargs["childData"]

    app.manager.setActiveWorkspace(parentID)
    app.editor.addWorkspace(id, name)

    wks = app.manager.workspace(id)
    wks.setGeometry(layoutToBBox(geometry))
    wks.setPadding(padding)

    if nodeGeometry:
        app.manager.scene().node(id).setPos(*nodeGeometry)

    for state in childData:
        restoreWorkspace(app, **state)


def restoreEdges(app, **kwargs):
    parentID = kwargs["parentID"]
    id = kwargs["ID"]
    edges: list[any] = kwargs.get("edges")
    childData = kwargs["childData"]

    app.manager.setActiveWorkspace(parentID)

    if edges:
        scene = app.manager.scene(parentID)
        for id2 in edges:
            app.editor.graphEditor.addEdge(scene, id, id2)

    for state in childData:
        restoreEdges(app, **state)


def restoreActions(app, **kwargs):
    id = kwargs["ID"]
    action = kwargs.get("action")
    childData = kwargs["childData"]

    if action:
        app.manager.setAction(id, action)

    for state in childData:
        restoreActions(app, **state)


def restoreRunner(app, **kwargs):
    state = RunnerState(**kwargs)
    app.runner.setState(state)


class AppSerializer(Serializer):
    def __init__(self, app):
        super().__init__(
            app,
            {
                "restoreWorkspace": restoreWorkspace,
                "restoreEdges": restoreEdges,
                "restoreActions": restoreActions,
                "restoreRunner": restoreRunner,
            },
        )

    def snapshot(self, data: AppState):
        serializedData = data.serialize()
        managerData = serializedData["managerState"]
        runnerData = serializedData["runnerState"]

        self.addLog("restoreWorkspace", managerData)
        self.addLog("restoreEdges", managerData)
        self.addLog("restoreActions", managerData)
        self.addLog("restoreRunner", runnerData)
