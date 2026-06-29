import numpy as np
from PIL import Image
from PyQt5.QtCore import QModelIndex, QSize, Qt
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import (
    QDialog,
    QFileDialog,
    QHeaderView,
    QLabel,
    QMenu,
    QTableView,
    QVBoxLayout,
)

from src.app.components.runtime.model import RuntimeModel, RuntimeType

from .delegate import RuntimeDelegate
from .model import RuntimeTableModel


class RuntimeTable(QTableView):
    def __init__(
        self,
        model: RuntimeModel,
        itemModel: RuntimeTableModel,
        delegate: RuntimeDelegate,
        parent=None,
    ):
        super().__init__(parent)

        self.model = model
        self.setModel(itemModel)
        self.setItemDelegate(delegate)

        self.setSelectionBehavior(QTableView.SelectRows)
        self.setSelectionMode(QTableView.SingleSelection)
        self.verticalHeader().hide()
        self.setAlternatingRowColors(True)
        self.setSortingEnabled(True)
        self.verticalHeader().setDefaultSectionSize(40)
        self.setIconSize(QSize(32, 32))

        header = self.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Fixed)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        self.setColumnWidth(1, 100)

        self.clicked.connect(self.onClick)
        self.doubleClicked.connect(self.onDoubleClick)

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

    def contextMenuEvent(self, event):
        index = self.indexAt(event.pos())

        if not index.isValid():
            return

        item = index.data(Qt.UserRole)
        menu = QMenu(self)

        if item.type == RuntimeType.IMAGE:
            save = menu.addAction("Save Image")
            action = menu.exec_(self.viewport().mapToGlobal(event.pos()))

            if action == save:
                self.saveSelectedImage()

    def saveSelectedImage(self):
        index = self.currentIndex()
        if not index.isValid():
            return

        item = index.data(Qt.UserRole)

        if item.type != RuntimeType.IMAGE or item.value is None:
            return

        path, _ = QFileDialog.getSaveFileName(
            self, "Save Image", f"{item.name}.png", "PNG (*.png);;JPG (*.jpg)"
        )

        if not path:
            return

        img = item.value

        Image.fromarray(img.astype(np.uint8)).save(path)
