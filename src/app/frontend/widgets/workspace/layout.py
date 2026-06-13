from src.app.frontend.state import Context, Document
from src.app.frontend.state.layouts import NodeItem

from .view import WorkspaceView


class LayoutController:
    def __init__(self, context: Context, document: Document, view: WorkspaceView):
        self.context = context
        self.document = document
        self.view = view

        self.view.workspaceCreated_.connect(self.updateLayout)
        self.view.workspaceChanged_.connect(self.updateLayout)
        self.view.workspacePressed_.connect(self.onWorkspacePressed)

        self.freeze = False

    def updateLayout(self, id):
        if self.freeze:
            return

        schema = self.view.getData(id)
        node = NodeItem(
            geometry=schema.geometry,
            displayText=schema.displayText,
            iconPath=schema.iconPath,
            padding=schema.padding,
        )
        self.document.workspace.nodes[id] = node

    def onWorkspacePressed(self, id):
        if self.freeze:
            return
        self.context.selectionModel.setSelected(id)

    def freezeLayout(self):
        self.freeze = True

    def unfreezeLayout(self):
        self.freeze = False
