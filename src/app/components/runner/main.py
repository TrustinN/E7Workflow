from src.app.backend.action import ActionRoute, ActionType
from src.app.frontend.events import Node
from src.app.frontend.state import Context, Document
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

        self.actionEditor = ActionEditor()
        self.actionEditor.requestSetAction.connect(self.requestActionSet)

        self.edgeEditor = EdgeEditor()
        self.edgeEditor.requestScript.connect(self.requestScript)
        self.edgeEditor.requestSetScript.connect(self.requestSetScript)
        self.edgeEditor.requestUnsetScript.connect(self.requestUnsetScript)

        self.scriptSync = ScriptSync(self.context, self.edgeEditor)

        self.runner = Runner(self.context, self.document, self.client)

        self.subscribe("/Workspace/Created", self.requestActionUnset)
        self.subscribe("/Runner/Execute/Requested", self.runner.execute)

        self.subscribe("/Runner/Script/Requested", self.handleScriptRequest)
        self.subscribe("/App/Reset", self.resetState)
        self.subscribe("/App/Import", self.loadState)

        self.addAction(ActionType.CLICK)
        self.addAction(ActionType.DRAG)

    def addAction(self, name):
        infoLink = Link(ActionRoute.NAME, ActionRoute.ACTION, name)
        info = self.client.get(infoLink)

        self.actionEditor.addAction(info)

    def requestActionSet(self):
        data = self.actionEditor.getActionData()
        self.publish("/Runner/Action/Set/Requested", data)

    def requestActionUnset(self, data):
        id = data["id"]
        parentID = self.context.workspaceModel.parent(id)
        self.publish("/Runner/Action/Unset/Requested", {"id": parentID})

    def requestScript(self):
        self.publish("/Runner/Script/Model/Requested", {})

    def requestSetScript(self):
        id = self.edgeEditor.currentEditor()
        self.publish("/Runner/Script/Model/Set/Requested", {"scriptID": id})

    def requestUnsetScript(self):
        self.publish("/Runner/Script/Model/Unset/Requested", {})

    def handleScriptRequest(self, data):
        id = data["id"]
        name = data["name"]
        self.edgeEditor.addCodeTab(id, name)
        self.publish("/Runner/Script/Created", data)

    def resetState(self, data):
        self.edgeEditor.clearState()
        self.scriptSync.clearState()

    def loadState(self, data):
        self.scriptSync.freezeState()
        for key in self.context.codeModel.keys():
            data = self.context.codeModel.getData(key)

            self.edgeEditor.setData(key, data)

        self.scriptSync.unfreezeState()
