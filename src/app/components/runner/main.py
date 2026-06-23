from src.app.events import Node
from src.app.state import Context, Document
from src.router.routing import Client, Dispatcher, Link

from .components import ActionEditor, EdgeEditor
from .runner import Runner
from .script import ScriptSync


class RunnerComponent(Node):
    def __init__(self, context: Context, document: Document, dispatcher: Dispatcher):
        super().__init__()

        self.context = context
        self.document = document
        self.client = Client("RunnerClient", dispatcher)

        self.runner = Runner(self.context, self.document, self.client)

        self.subscribe("/Workspace/Created", self.requestActionUnset)
        self.subscribe("/Runner/Execute/Requested", self.runner.execute)

        self.subscribe("/Runner/Script/Requested", self.handleScriptRequest)
        self.subscribe("/App/Reset", self.resetState)
        self.subscribe("/App/Import", self.loadState)

    #
    # def resetState(self, data):
    #     self.edgeEditor.clearState()
    #     self.scriptSync.clearState()
    #
    # def loadState(self, data):
    #     self.scriptSync.freezeState()
    #     for key in self.context.codeModel.keys():
    #         data = self.context.codeModel.getData(key)
    #
    #         self.edgeEditor.setData(key, data)
    #
    #     self.scriptSync.unfreezeState()
