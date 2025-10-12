from src.app.frontend.context import ContextManager

RUNNER_CTX = "RUNNER CTX"


class RunnerContextManager:
    def __init__(self, ctxManager: ContextManager):
        self.context = ctxManager.addContext(RUNNER_CTX)
        self.context.add("localEntries", {})
        self.context.add("globalEntry", None)

    def getData(self):
        return self.context.toDict()

    def setLocalEntry(self, data):
        parentID = data.get("parentID")
        entryID = data.get("entryID")

        self.context.get("localEntries")[parentID] = entryID

    def setGlobalEntry(self, data):
        globalID = data.get("globalID")

        self.context.put("globalEntry", globalID)
