from PyQt5.QtWidgets import QVBoxLayout, QWidget

from .nodes import GraphMiniView
from .widgets import GraphButtonsWidget, GraphViewWidget


class GraphComponent(QWidget):

    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.buttons = GraphButtonsWidget()
        self.miniView = GraphViewWidget()

        self.miniViewNode = GraphMiniView(self.miniView, self.buttons)

        self.layout.addWidget(self.miniView)
        self.layout.addWidget(self.buttons)
