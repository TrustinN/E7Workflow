from PyQt5.QtWidgets import QPushButton, QVBoxLayout, QWidget

from .node import SerializationNode


class SerializationComponent(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.exportBtn = QPushButton("Export Workspace")
        self.importBtn = QPushButton("Import Workspace")

        self.layout.addWidget(self.exportBtn)
        self.layout.addWidget(self.importBtn)

        self.node = SerializationNode()

        self.exportBtn.clicked.connect(self.handleExport)
        self.importBtn.clicked.connect(self.handleImport)

    def handleExport(self):
        self.node.requestExport()

    def handleImport(self):
        self.node.requestReset()
        self.node.requestImport()
