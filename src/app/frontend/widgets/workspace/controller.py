import os

from src.app.config import ICON_DIR
from src.app.frontend.state import Context, Document
from src.app.frontend.state.layouts.graph import Color
from src.app.frontend.widgets.utils.colors import Alpha, Colors, with_alpha

from .components import WorkspaceSchema
from .view import WorkspaceView


class WorkspaceController:
    def __init__(self, context: Context, document: Document, view: WorkspaceView):
        self.context = context
        self.document = document
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

        self.context.selectionModel.selected_.connect(self.onSelection)

    def _createRootWorkspace(self, id):
        self.view.createRootWorkspace(id)

        schema = WorkspaceSchema(displayText="Root", padding=15)
        self.view.setData(id, schema)

    def _createChildWorkspace(self, id, parentID):
        data = self.context.workspaceModel.nodeData(id)

        text = f"{data["grouping"]} - {data["text"]}"
        schema = WorkspaceSchema(displayText=text)

        self.view.createChildWorkspace(id, parentID)
        self.view.setData(id, schema)

    def createWorkspace(self, id):
        parentID = self.context.workspaceModel.parent(id)
        if parentID is None:
            self._createRootWorkspace(id)
        else:
            self._createChildWorkspace(id, parentID)

    def onSelection(self, id):
        prevID = self.context.selectionModel.getPrevSelected()
        if prevID:
            color = Colors.DEFAULT_COLOR
            borderColor = Colors.DEFAULT_BORDER
            schema = WorkspaceSchema(
                color=Color(*color.getRgb()),
                borderColor=Color(*borderColor.getRgb()),
            )
            self.view.setData(prevID, schema)

        if id:
            color = with_alpha(Colors.SKY_BLUE, Alpha.LIGHT)
            borderColor = with_alpha(Colors.SKY_BLUE, Alpha.MEDIUM)
            schema = WorkspaceSchema(
                color=Color(*color.getRgb()),
                borderColor=Color(*borderColor.getRgb()),
            )
            self.view.setData(id, schema)

    def rerenderView(self):
        schemas = {}
        for nodeID in list(self.context.workspaceModel.nodeIter())[::-1]:
            data = self.document.workspace.nodes[nodeID]
            schema = WorkspaceSchema(
                displayText=data.displayText,
                geometry=data.geometry,
                iconPath=data.iconPath,
                padding=data.padding,
                color=data.color,
                borderColor=data.borderColor,
            )
            schemas[nodeID] = schema
            self.view.setData(nodeID, schema)

    def recreateView(self):
        for nodeID in self.context.workspaceModel.nodeIter():
            if self.context.workspaceModel.isRoot(nodeID):
                self._createRootWorkspace(nodeID)
            else:
                parentID = self.context.workspaceModel.parent(nodeID)
                self._createChildWorkspace(nodeID, parentID)

        self.rerenderView()

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
