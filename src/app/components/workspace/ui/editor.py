from PyQt5.QtWidgets import (
    QFormLayout,
    QGroupBox,
    QInputDialog,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from src.app.actions import ActionRegistry
from src.app.components.workspace.model import WorkspaceModel
from src.app.state import Context, Geometry, Selection, SelectionType

from .controller import WorkspaceController
from .view import WorkspaceView


class WorkspaceInspector(QWidget):
    def __init__(self, context: Context, model: WorkspaceModel):
        super().__init__()

        self.model = model
        self.context = context
        self.context.selectionModel.selected_.connect(self.onItemSelection)

        self.currentID = None

        layout = QVBoxLayout(self)

        self.nameEdit = QLineEdit()
        self.nameEdit.textChanged.connect(self.onNameChanged)

        geomGroup = QGroupBox("Geometry")
        geomLayout = QFormLayout(geomGroup)

        self.xSpin = QSpinBox()
        self.ySpin = QSpinBox()
        self.wSpin = QSpinBox()
        self.hSpin = QSpinBox()

        for spin in (
            self.xSpin,
            self.ySpin,
            self.wSpin,
            self.hSpin,
        ):
            spin.setRange(-100000, 100000)
            spin.valueChanged.connect(self.onGeometryChanged)

        geomLayout.addRow("X", self.xSpin)
        geomLayout.addRow("Y", self.ySpin)
        geomLayout.addRow("Width", self.wSpin)
        geomLayout.addRow("Height", self.hSpin)

        form = QFormLayout()
        form.addRow("Name", self.nameEdit)

        layout.addLayout(form)
        layout.addWidget(geomGroup)
        layout.addStretch()

        self.model.modelUpdated.connect(self.onModelUpdated)
        self.model.modelDeleted.connect(self.onModelDeleted)

    def onItemSelection(self, selection: Selection):
        if not (selection.id and selection.type == SelectionType.WORKSPACE):
            self.setWorkspace(None)
            return

        self.setWorkspace(selection.id)

    def setWorkspace(self, workspaceID):
        self.currentID = workspaceID
        self.refresh()

    def refresh(self):
        if self.currentID is None:
            self.setEnabled(False)
            return

        self.setEnabled(True)

        schema = self.model.getItem(self.currentID)

        self.nameEdit.blockSignals(True)
        self.nameEdit.setText(schema.name)
        self.nameEdit.blockSignals(False)

        for widget, value in [
            (self.xSpin, schema.geometry.x),
            (self.ySpin, schema.geometry.y),
            (self.wSpin, schema.geometry.width),
            (self.hSpin, schema.geometry.height),
        ]:
            widget.blockSignals(True)
            widget.setValue(value)
            widget.blockSignals(False)

    def onNameChanged(self):
        if self.currentID is None:
            return

        self.model.updateItem(
            self.currentID,
            {"name": self.nameEdit.text()},
        )

    def onGeometryChanged(self):
        if self.currentID is None:
            return

        geom = Geometry(
            x=self.xSpin.value(),
            y=self.ySpin.value(),
            width=self.wSpin.value(),
            height=self.hSpin.value(),
        )

        self.model.updateItem(
            self.currentID,
            {"geometry": geom},
        )

    def onModelUpdated(self, workspaceID):
        if workspaceID == self.currentID:
            self.refresh()

    def onModelDeleted(self, workspaceID):
        if workspaceID == self.currentID:
            self.setWorkspace(None)


class WorkspaceEditor(QWidget):
    def __init__(
        self, context: Context, model: WorkspaceModel, actions: ActionRegistry
    ):
        super().__init__()
        self.layout = QVBoxLayout(self)

        self.context = context
        self.view = WorkspaceView(model)
        self.controller = WorkspaceController(context, self.view, model)

        action = actions.get("Create Workspace")
        self.createBtn = QPushButton(actions.displayText("Create Workspace"))
        self.createBtn.clicked.connect(action.trigger)

        action = actions.get("Delete Workspace")
        self.deleteBtn = QPushButton(actions.displayText("Delete Workspace"))
        self.deleteBtn.clicked.connect(action.trigger)

        self.inspector = WorkspaceInspector(context, model)

        self.layout.addWidget(self.createBtn)
        self.layout.addWidget(self.deleteBtn)
        self.layout.addWidget(self.inspector)
        self.layout.addStretch()
