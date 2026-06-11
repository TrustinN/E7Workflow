import os

from src.app.config import ICON_DIR
from src.app.frontend.state import WorkspaceContext
from src.app.frontend.widgets.utils.colors import Alpha, Colors, with_alpha

from .view import WorkspaceView


class WorkspaceController:
    def __init__(self, context: WorkspaceContext, view: WorkspaceView):
        self.context = context
        self.view = view

        self.iconPaths = {
            "Click": os.path.join(ICON_DIR, "mouse-pointer-click.svg"),
            "Drag.down": os.path.join(ICON_DIR, "move-down.svg"),
            "Drag.left": os.path.join(ICON_DIR, "move-left.svg"),
            "Drag.right": os.path.join(ICON_DIR, "move-right.svg"),
            "Drag.up": os.path.join(ICON_DIR, "move-up.svg"),
        }

        self.context.workspaceModel.nodeCreated_.connect(self.createWorkspace)
        self.context.actionModel.dataSet_.connect(self.onActionBind)
        self.context.actionModel.dataRemoved_.connect(self.onActionUnbind)
        self.context.modelClear_.connect(self.clearState)
        self.context.modelLoaded_.connect(self.recreateView)

        self.view.workspacePressed_.connect(self.onWorkspacePressed)
        self.view.workspaceChanged_.connect(self.updateModelGeometry)

        self.context.selectionModel.selected_.connect(self.onSelection)

    def _createRootWorkspace(self, id):
        self.view.createRootWorkspace(id)
        self.view.setPadding(id, 15)
        self.view.setName(id, "Root")

    def _createChildWorkspace(self, id, parentID):
        data = self.context.workspaceModel.nodeData(id)
        name = f"{data["grouping"]} - {data["text"]}"

        self.view.createChildWorkspace(id, parentID)
        self.view.setName(id, name)

    def createWorkspace(self, id):
        parentID = self.context.workspaceModel.parent(id)
        if parentID is None:
            self._createRootWorkspace(id)
        else:
            self._createChildWorkspace(id, parentID)

    def onSelection(self, id):
        prevID = self.context.selectionModel.getPrevSelected()
        if prevID:
            self.view.setColor(
                prevID,
                Colors.DEFAULT_COLOR,
                Colors.DEFAULT_BORDER,
            )

        if id:
            self.view.setColor(
                id,
                with_alpha(Colors.SKY_BLUE, Alpha.LIGHT),
                with_alpha(Colors.SKY_BLUE, Alpha.MEDIUM),
            )

    def onWorkspacePressed(self, id):
        self.context.selectionModel.setSelected(id)

    def updateModelGeometry(self, id):
        data = self.context.workspaceModel.nodeData(id)
        geometry = self.view.getGeometry(id)
        data.update({"geometry": geometry})
        self.context.workspaceModel.updateNode(id, data)

    def rerenderView(self):
        for nodeID in self.context.workspaceModel.nodeIter():
            data = self.context.workspaceModel.nodeData(nodeID)
            geometry = data["geometry"]
            self.view.setGeometry(nodeID, geometry)

    def recreateView(self):
        self.view.workspaceChanged_.disconnect(self.updateModelGeometry)

        for nodeID in self.context.workspaceModel.nodeIter():
            if self.context.workspaceModel.isRoot(nodeID):
                self._createRootWorkspace(nodeID)
            else:
                parentID = self.context.workspaceModel.parent(nodeID)
                self._createChildWorkspace(nodeID, parentID)

        self.rerenderView()
        self.view.workspaceChanged_.connect(self.updateModelGeometry)

    def clearState(self):
        self.view.clearState()

    def getIconPath(self, data):
        name = data["name"]
        if name == "Click":
            return self.iconPaths[name]
        elif name == "Drag":
            userParams = data["userParams"]
            direction = userParams["dir"]["value"]
            return self.iconPaths[f"{name}.{direction}"]

    def onActionBind(self, id):
        data = self.context.actionModel.getData(id)
        self.view.setIcon(id, self.getIconPath(data))

    def onActionUnbind(self, id):
        self.view.setIcon(id, "")
