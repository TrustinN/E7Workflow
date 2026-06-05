from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGraphicsView, QPushButton, QVBoxLayout, QWidget


class GraphButtonsWidget(QWidget):

    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.setE1Btn = QPushButton("SetEdgeStart")
        self.setE2Btn = QPushButton("SetEdgeEnd")
        self.createEdgeBtn = QPushButton("Create Edge")

        self.layout.addWidget(self.setE1Btn)
        self.layout.addWidget(self.setE2Btn)
        self.layout.addWidget(self.createEdgeBtn)
