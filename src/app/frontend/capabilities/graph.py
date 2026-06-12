from nanoid import generate

from src.app.frontend.events import Node


class GraphCapability(Node):
    def __init__(self):
        super().__init__()

    def createEdge(self):
        data = {"id": generate()}
        self.publish("/Graph/EdgeRequested", data)
