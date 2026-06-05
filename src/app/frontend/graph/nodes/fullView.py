from nanoid import generate

from src.app.frontend.events import Node
from src.app.frontend.graph.components import GraphMV, GraphSerializer
from src.app.frontend.graph.widgets import GraphButtonsWidget, GraphViewWidget


class GraphFullView(Node):
    def __init__(self, view: GraphViewWidget, buttons: GraphButtonsWidget):
        self.buttons = buttons
        self.view = view
        pass
