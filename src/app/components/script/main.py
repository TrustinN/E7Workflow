from src.app.events import Node

from .ui import ScriptManager


class ScriptComponent(Node):
    def __init__(self):
        super().__init__()

        self.editor = ScriptManager()
        self.editor.requestScript.connect(self.createScript)
        self.editor.requestSetScript.connect(self.setScript)
        self.editor.requestUnsetScript.connect(self.unsetScript)

    # def requestScript(self):
    #     self.publish("/Runner/Script/Model/Requested", {})
    #
    # def requestSetScript(self):
    #     id = self.edgeEditor.currentEditor()
    #     self.publish("/Runner/Script/Model/Set/Requested", {"scriptID": id})
    #
    # def requestUnsetScript(self):
    #     self.publish("/Runner/Script/Model/Unset/Requested", {})
    #
    # def handleScriptRequest(self, data):
    #     id = data["id"]
    #     name = data["name"]
    #     self.edgeEditor.addCodeTab(id, name)
    #     self.publish("/Runner/Script/Created", data)
