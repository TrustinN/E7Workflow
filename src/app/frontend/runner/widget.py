from PyQt5.QtWidgets import QPushButton, QVBoxLayout, QWidget


class RunnerWidget(QWidget):

    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.setLocalEntryBtn = QPushButton("Set Local Entry")
        self.setGlobalEntryBtn = QPushButton("Set Global Entry")
        self.restoreRunnerBtn = QPushButton("Restore Runner")

        self.layout.addWidget(self.setLocalEntryBtn)
        self.layout.addWidget(self.setGlobalEntryBtn)
        self.layout.addWidget(self.restoreRunnerBtn)
