from PyQt5.QtWidgets import QPushButton, QVBoxLayout, QWidget


class GraphButtons(QWidget):

    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.setE1Btn = QPushButton("SetEdgeStart")
        self.setE2Btn = QPushButton("SetEdgeEnd")

        self.layout.addWidget(self.setE1Btn)
        self.layout.addWidget(self.setE2Btn)
