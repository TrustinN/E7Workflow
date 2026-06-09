from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGraphicsView, QVBoxLayout, QWidget

from src.app.frontend.widgets.graph.components.scene import GraphScene


class GraphView(QWidget):

    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.view = QGraphicsView()
        self.view.setFixedSize(400, 300)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.layout.addWidget(self.view)

    @property
    def scene(self) -> GraphScene:
        return self.view.scene()

    def setScene(self, scene):
        self.view.setScene(scene)
