from src.app.frontend.state import Document
from src.app.frontend.state.layouts import NodeItem

from .components import WorkspaceSchema
from .view import WorkspaceView


class WorkspaceLayoutSync:
    def __init__(self, document: Document, view: WorkspaceView):
        self.document = document
        self.view = view

        self.view.workspaceCreated_.connect(self.updateLayout)
        self.view.workspaceChanged_.connect(self.updateLayout)

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

    def freezeLayout(self):
        self.freeze = True

    def unfreezeLayout(self):
        self.freeze = False

    def rerenderView(self):
        for nodeID in list(self.document.workspace.nodes)[::-1]:
            data = self.document.workspace.nodes[nodeID]
            schema = WorkspaceSchema(
                displayText=data.displayText,
                geometry=data.geometry,
                iconPath=data.iconPath,
                padding=data.padding,
                color=data.color,
                borderColor=data.borderColor,
            )
            self.view.setData(nodeID, schema)

    def resetState(self):
        self.freeze = False
