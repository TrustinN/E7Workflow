from nanoid import generate

from src.app.frontend.events import Node
from src.app.frontend.state import Context


class GraphCapability(Node):
    def __init__(self, context: Context):
        super().__init__()
        self.context = context

        self.subscribe("/Graph/Root/Created", self.onRootCreated)

    def createEdge(self):
        data = {"id": generate()}
        self.publish("/Graph/EdgeRequested", data)

    def onRootCreated(self, data):
        id = data["id"]
        self.context.selectionModel.setSelected(id)
