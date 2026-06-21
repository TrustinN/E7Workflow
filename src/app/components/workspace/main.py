from nanoid import generate
from PyQt5.QtWidgets import QInputDialog, QLineEdit

from src.app.events import Node
from src.app.state import Context, SelectionType

from .model import WorkspaceModel, WorkspaceSchema
from .ui import WorkspaceController, WorkspaceScreen, WorkspaceView


class WorkspaceComponent(Node):
    def __init__(self, context: Context):
        super().__init__()

        self.context = context
        self.model = WorkspaceModel()
        self.view = WorkspaceView(self.model)
        self.controller = WorkspaceController(self.context, self.view, self.model)
        self.screen = WorkspaceScreen()
        self.screen.btn.clicked.connect(self.createWorkspace)
        self.screen.shortcut.activated.connect(self.createWorkspace)

        self.availableGroups = set(chr(ord("A") + i) for i in range(26))
        self.groupAssignments = {}

        self.subscribe("/App/Loaded", self.createRootWorkspace)

    def createRootWorkspace(self, data):
        id = generate()
        schema = WorkspaceSchema(id=id, displayText="Root", padding=15)

        self.model.addItem(id, schema)
        self.publish("/Workspace/Root/Created", schema.toData())

    def createWorkspace(self):
        id = generate()
        selection = self.context.selectionModel.getSelected()
        if not (selection.id and selection.type is SelectionType.WORKSPACE):
            return
        parentID = selection.id

        name = self.requestWorkspaceName()
        if not name:
            return
        group = self.assignGroup(id, parentID)
        schema = WorkspaceSchema(
            id=id,
            displayText=name,
            grouping=group,
            padding=0,
            parent=parentID,
        )

        self.model.addItem(id, schema)
        self.publish("/Workspace/Node/Created", schema.toData())

    def requestWorkspaceName(self):
        name, ok = QInputDialog.getText(
            None,
            "QInputDialog.getText()",
            "Workspace Name:",
            QLineEdit.Normal,
            "WS Name",
        )
        if not ok:
            return False

        return name

    def popGroup(self):
        group = min(self.availableGroups)
        self.availableGroups.remove(group)
        return group

    def assignGroup(self, id, parentID):
        group = None
        if self.model.rootIndex() == parentID:
            group = self.popGroup()
            self.groupAssignments[id] = group

        else:
            group = self.groupAssignments[parentID]
            self.groupAssignments[id] = group

        return group

    def resetState(self, data):
        self.availableGroups = set(chr(ord("A") + i) for i in range(26))
        self.groupAssignments = {}

    # def loadState(self, data):
    #     for nodeID in self.context.workspaceModel.nodeIter():
    #         if self.context.workspaceModel.isRoot(nodeID):
    #             continue
    #
    #         grouping = self.context.workspaceModel.nodeData(nodeID)["grouping"]
    #         self.groupAssignments[nodeID] = grouping
    #         self.availableGroups.discard(grouping)
