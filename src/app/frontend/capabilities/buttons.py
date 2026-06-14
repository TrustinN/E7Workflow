from PyQt5.QtWidgets import QPushButton, QVBoxLayout, QWidget


class Buttons(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.workspaceBtn = QPushButton("Create Workspace")
        self.setE1Btn = QPushButton("SetEdgeStart")
        self.setE2Btn = QPushButton("SetEdgeEnd")
        self.createEdgeBtn = QPushButton("Create Edge")
        self.entryBtn = QPushButton("Set Entry")
        self.executeBtn = QPushButton("Execute")

        self.exportBtn = QPushButton("Export")
        self.importBtn = QPushButton("Import")

        self.layout.addWidget(self.workspaceBtn)
        self.layout.addWidget(self.setE1Btn)
        self.layout.addWidget(self.setE2Btn)
        self.layout.addWidget(self.createEdgeBtn)
        self.layout.addWidget(self.entryBtn)
        self.layout.addWidget(self.executeBtn)

        self.layout.addWidget(self.exportBtn)
        self.layout.addWidget(self.importBtn)
