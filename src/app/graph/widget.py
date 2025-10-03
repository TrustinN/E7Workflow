from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGraphicsView, QPushButton, QVBoxLayout, QWidget


class GraphWidget(QWidget):

    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.view = QGraphicsView()
        self.view.setFixedSize(400, 300)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.createEdgeBtn = QPushButton("Create Edge")

        self.layout.addWidget(self.view)
        self.layout.addWidget(self.createEdgeBtn)

    @property
    def scene(self):
        return self.view.scene()

    def setScene(self, scene):
        self.view.setScene(scene)
