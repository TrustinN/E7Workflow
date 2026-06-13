from src.app.frontend.state import Context

from .components import WorkspaceSchema
from .view import WorkspaceView


class WorkspaceBuilder:
    def __init__(self, context: Context, view: WorkspaceView):
        self.context = context
        self.view = view

        self.context.workspaceModel.nodeCreated_.connect(self.createWorkspace)

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

    def recreateView(self):
        for nodeID in self.context.workspaceModel.nodeIter():
            if self.context.workspaceModel.isRoot(nodeID):
                self._createRootWorkspace(nodeID)
            else:
                parentID = self.context.workspaceModel.parent(nodeID)
                self._createChildWorkspace(nodeID, parentID)
