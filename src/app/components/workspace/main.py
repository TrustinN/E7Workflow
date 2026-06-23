import json
import os

from nanoid import generate
from PyQt5.QtWidgets import QInputDialog, QLineEdit

from src.app.events import Node
from src.app.state import Context, SelectionType

from .model import WorkspaceModel, WorkspaceSchema
from .ui import WorkspaceEditor


class WorkspaceComponent(Node):
    def __init__(self, context: Context):
        super().__init__()

        self.context = context
        self.model = WorkspaceModel()
        self.editor = WorkspaceEditor(self.context, self.model)
        self.editor.requestWorkspace.connect(self.createWorkspace)

        self.subscribe("/App/Loaded", self.createRootWorkspace)
        self.subscribe("/App/Export", self.saveState)
        self.subscribe("/App/Reset", self.resetState)
        self.subscribe("/App/Import", self.loadState)

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
        schema = WorkspaceSchema(
            id=id,
            displayText=name,
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

    def saveState(self, data):
        path = data["path"]
        saveFile = os.path.join(path, "workspace.json")
        state = self.model.toData()
        with open(saveFile, "w") as f:
            json.dump(state, f, indent=4)

    def resetState(self, data):
        self.model.clear()

    def loadState(self, data):
        path = data["path"]
        saveFile = os.path.join(path, "workspace.json")
        state = None
        with open(saveFile, "r") as f:
            state = json.load(f)

        self.model.fromData(state)
