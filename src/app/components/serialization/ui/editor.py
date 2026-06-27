from PyQt5.QtCore import QDir, pyqtSignal
from PyQt5.QtWidgets import (
    QFileSystemModel,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QTreeView,
    QVBoxLayout,
    QWidget,
)

from src.app.config import SAVE_DIR


class SerializerEditor(QWidget):
    exportRequested = pyqtSignal(str)
    importRequested = pyqtSignal(str)

    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout(self)

        dir = QDir(QDir.currentPath())
        dir.mkdir(SAVE_DIR)
        self.rootPath = dir.filePath(SAVE_DIR)

        exportLayout = QHBoxLayout()

        self.nameEdit = QLineEdit(self)
        self.nameEdit.setPlaceholderText("Project name")

        self.exportBtn = QPushButton("Export", self)
        self.exportBtn.clicked.connect(self.onExport)

        exportLayout.addWidget(self.nameEdit)
        exportLayout.addWidget(self.exportBtn)

        self.model = QFileSystemModel(self)
        self.model.setRootPath(self.rootPath)

        self.tree = QTreeView(self)
        self.tree.setModel(self.model)
        self.tree.setRootIndex(self.model.index(self.rootPath))
        self.tree.selectionModel().selectionChanged.connect(self.updateButtons)

        for col in range(1, self.model.columnCount()):
            self.tree.hideColumn(col)

        importLayout = QHBoxLayout()
        importLayout.addStretch()

        self.importBtn = QPushButton("Import", self)
        self.importBtn.clicked.connect(self.onImport)
        self.importBtn.setEnabled(False)

        importLayout.addWidget(self.importBtn)

        self.layout.addLayout(exportLayout)
        self.layout.addWidget(self.tree)
        self.layout.addLayout(importLayout)

    def selectedPath(self):
        index = self.tree.currentIndex()
        if not index.isValid():
            return None
        return self.model.filePath(index)

    def isTopLevelFolder(self, path):
        if path is None:
            return False

        index = self.model.index(path)

        if not self.model.isDir(index):
            return False

        parent = QDir(path)
        parent.cdUp()

        return parent.absolutePath() == QDir(self.rootPath).absolutePath()

    def updateButtons(self):
        self.importBtn.setEnabled(self.isTopLevelFolder(self.selectedPath()))

    def onExport(self):
        name = self.nameEdit.text().strip()
        if not name:
            return

        path = QDir(self.rootPath).filePath(name)
        self.exportRequested.emit(path)

    def onImport(self):
        path = self.selectedPath()
        if self.isTopLevelFolder(path):
            self.importRequested.emit(path)
