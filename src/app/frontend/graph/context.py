from src.app.frontend.context import Context, ContextManager

GRAPH_CTX = "GRAPH CTX"


class GraphContextManager:
    def __init__(self, context: Context):
        self.context = context
        self.context.add("activeScene", None)
        self.context.add("activeNode", None)
        self.context.add("sceneParents", {})
        self.context.add("workspaceViewMapping", {})
        self.context.add("workspaceNodeMapping", {})

    def getData(self):
        return self.context.toDict()

    def updateActiveScene(self, data):
        sceneID = data.get("sceneID")
        self.context.put("activeScene", sceneID)

    def updateSceneParents(self, data):
        sceneID = data.get("sceneID")

        activeID = self.context.get("activeScene")
        if activeID:
            self.context.get("sceneParents")[sceneID] = activeID

    def updateSceneBinding(self, data):
        wksID = data.get("id")
        sceneID = data.get("sceneID")

        self.context.get("workspaceViewMapping")[wksID] = sceneID

    def updateNodeBinding(self, data):
        wksID = data.get("id")
        nodeID = data.get("nodeID")

        self.context.get("workspaceNodeMapping")[wksID] = nodeID
