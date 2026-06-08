from PyQt5.QtWidgets import QPushButton, QVBoxLayout, QWidget


class RunnerButtons(QWidget):

    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.executeBtn = QPushButton("Execute")

        self.layout.addWidget(self.executeBtn)
