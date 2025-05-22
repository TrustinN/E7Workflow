class WorkflowState(dict):
    def __init__(self):
        super().__init__()

    def setState(self, name, value):
        self[name] = value

    def getState(self, name):
        return self[name]


class GlobalState(dict):
    def __init__(self):
        super().__init__()

    def addWorkflowState(self, name: str):
        self[name] = WorkflowState()

    def getWorkflowState(self, name: str) -> WorkflowState:
        return self[name]


class StateManager:
    def __init__(self, scope):
        self.scope = scope

    def initState(self, state: GlobalState):
        state.addWorkflowState(self.scope)

    def getScope(self):
        return self.scope
