from nanoid import generate


class RunnerBackend:
    def __init__(self):
        self.states = {}
        self.transitions = {}
        self.stateActions = {}
        self.actions = {}

    def createState(self, data=None):
        data = data or {}

        stateID = generate()
        self.states[stateID] = data
        self.stateActions[stateID] = data.get("actionID")
        return stateID, data

    def updateState(self, stateID, data):
        self.states[id].update(data)
        self.stateActions[stateID] = data.get("actionID")

    def createAction(self, data=None):
        data = data or {}

        actionID = generate()
        self.actions[actionID] = data
        return actionID

    def updateAction(self, actionID, data):
        self.actions[actionID].update(data)

    def createTransition(self, state1, state2, data):
        self.transitions[state1] = state2

    def clear(self):
        self.states.clear()
        self.transitions.clear()
        self.actions.clear()

    # def overwrite(self, data):
    #     self.workspaces = data
