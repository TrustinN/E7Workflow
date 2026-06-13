from nanoid import generate

from src.app.frontend.events import Node
from src.app.frontend.state import Context


class GraphCapability(Node):
    def __init__(self, context: Context):
        super().__init__()
        self.context = context

        self.firstEdge = None
        self.secondEdge = None

        self.subscribe("/Workspace/Root/Created", self.requestRoot)
        self.subscribe("/Workspace/Created", self.requestNode)
        self.subscribe("/Graph/Root/Created", self.onRootCreated)
        self.subscribe("/App/Reset", self.resetState)

    def setE1(self):
        self.firstEdge = self.context.selectionModel.getSelected()

    def setE2(self):
        self.secondEdge = self.context.selectionModel.getSelected()

    def requestRoot(self, data):
        id = data["id"]
        self.context.graphModel.createNode(id, data)
        self.publish("/Graph/Root/Requested", data)

    def requestNode(self, data):
        id = data["id"]
        self.context.graphModel.createNode(id, data)
        self.publish("/Graph/Node/Requested", data)

    def requestEdge(self):
        id = generate()
        cond1 = self.firstEdge is not None
        cond2 = self.secondEdge is not None
        cond3 = self.firstEdge != self.secondEdge
        if not (cond1 and cond2 and cond3):
            return

        self.context.graphModel.createEdge(id, self.firstEdge, self.secondEdge, {})
        data = {"id": id, "start": self.firstEdge, "end": self.secondEdge}
        self.publish("/Graph/Edge/Requested", data)

        self.firstEdge = None
        self.secondEdge = None

    def onRootCreated(self, data):
        id = data["id"]
        self.context.selectionModel.setSelected(id)

    def resetState(self, data):
        self.firstEdge = None
        self.secondEdge = None
