import numpy as np
from PIL import Image
from PyQt5.QtCore import QModelIndex, QSize, Qt
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import (
    QComboBox,
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from src.app.components.runtime.model import RuntimeModel, RuntimeSchema, RuntimeType

from .delegate import RuntimeDelegate
from .model import RuntimeTableModel


class RuntimeEditor(QWidget):
    def __init__(self, model: RuntimeModel):
        super().__init__()

        self.model = model
        self.tableModel = RuntimeTableModel(model)
        self.delegate = RuntimeDelegate()

        self.currentKey = None

        self.layout = QVBoxLayout(self)

        self.table = QTableView()
        self.table.setModel(self.tableModel)
        self.table.setItemDelegate(self.delegate)

        self.table.setSelectionBehavior(QTableView.SelectRows)
        self.table.setSelectionMode(QTableView.SingleSelection)
        self.table.verticalHeader().hide()
        self.table.setAlternatingRowColors(True)
        self.table.setSortingEnabled(True)
        self.table.verticalHeader().setDefaultSectionSize(40)
        self.table.setIconSize(QSize(32, 32))

        self.table.clicked.connect(self.onClick)
        self.table.doubleClicked.connect(self.onDoubleClick)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Fixed)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        self.table.setColumnWidth(1, 100)

        controls = QHBoxLayout()

        self.line = QLineEdit()
        self.line.setPlaceholderText("Variable name")

        self.combo = QComboBox()
        for rt in RuntimeType:
            self.combo.addItem(rt.name, rt)

        self.addBtn = QPushButton("+ Add")
        self.deleteBtn = QPushButton("− Delete")

        self.addBtn.clicked.connect(self.handleVariableAdd)
        self.deleteBtn.clicked.connect(self.handleVariableDelete)

        controls.addWidget(self.line, 1)
        controls.addWidget(self.combo)
        controls.addWidget(self.addBtn)
        controls.addWidget(self.deleteBtn)

        self.layout.addWidget(self.table)
        self.layout.addLayout(controls)

    def handleVariableAdd(self):
        runtimeType = self.combo.currentData()
        name = self.line.text()

        if name:
            self.model.addItem(name, RuntimeSchema(name=name, type=runtimeType))

    def handleVariableDelete(self):
        indexes = self.table.selectionModel().selectedRows()

        if not indexes:
            return

        row = indexes[0].row()
        key = self.tableModel.keys[row]
        self.model.deleteItem(key)

    def onDoubleClick(self, index: QModelIndex):
        item = index.data(Qt.ItemDataRole.UserRole)

        if item.type == RuntimeType.IMAGE:
            path, _ = QFileDialog.getOpenFileName(
                self, "Select Image", "", "Images (*.png *.jpg *.jpeg *.svg)"
            )

            if path:
                image = np.array(Image.open(path).convert("RGB"))
                self.model.updateItem(item.name, {"value": image})

    def onClick(self, index: QModelIndex):
        item = index.data(Qt.UserRole)

        if item.type != RuntimeType.IMAGE or item.value is None:
            return

        img = item.value  # numpy array HxWx3

        h, w, _ = img.shape
        qimg = QImage(
            img.data,
            w,
            h,
            img.strides[0],
            QImage.Format_RGB888,
        )

        pixmap = QPixmap.fromImage(qimg)

        dialog = QDialog(self)
        dialog.setWindowTitle(item.name)

        label = QLabel()
        label.setAlignment(Qt.AlignCenter)
        label.setPixmap(
            pixmap.scaled(
                800,
                600,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation,
            )
        )

        layout = QVBoxLayout(dialog)
        layout.addWidget(label)

        dialog.resize(800, 600)
        dialog.exec_()
