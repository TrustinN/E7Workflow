from src.app.backend.action import ActionRoute, ActionType
from src.app.frontend.events import Node
from src.app.frontend.state import Context, Document
from src.router.routing import Client, Dispatcher, Link

from .runner import Runner
from .widget import RunnerWidget


class RunnerComponent(Node):
    def __init__(self, context: Context, document: Document, dispatcher: Dispatcher):
        super().__init__()

        self.context = context
        self.document = document
        self.client = Client("RunnerClient", dispatcher)

        self.widget = RunnerWidget()
        self.widget.actionBtn.clicked.connect(self.requestActionSet)

        self.runner = Runner(self.context, self.document, self.client)

        self.subscribe("/Workspace/Created", self.requestActionUnset)
        self.subscribe("/Runner/Execute/Requested", self.runner.execute)

        self.addAction(ActionType.CLICK)
        self.addAction(ActionType.DRAG)

    def addAction(self, name):
        infoLink = Link(ActionRoute.NAME, ActionRoute.ACTION, name)
        info = self.client.get(infoLink)

        self.widget.addAction(info)

    def requestActionSet(self):
        data = self.widget.getActionData()
        self.publish("/Runner/Action/Set/Requested", data)

    def requestActionUnset(self, data):
        id = data["id"]
        parentID = self.context.workspaceModel.parent(id)
        self.publish("/Runner/Action/Unset/Requested", {"id": parentID})
