from enum import Enum

from workflows.state import StateManager


class InventoryManager(StateManager):

    def __init__(self, scope, items: Enum):
        super().__init__(scope)
        self.items = items

    def initState(self):
        super().initState()
        mState = self.state.getWorkflowState(self.scope)
        for item in self.items:
            mState.setState(item, 0)

    def subtractAmount(self, item, amount):
        assert amount >= 0

        mState = self.state.getWorkflowState(self.scope)
        curAmt = mState.getState(item)
        curAmt -= amount
        mState.setState(item, curAmt)

    def addAmount(self, item, amount):
        assert amount >= 0

        mState = self.state.getWorkflowState(self.scope)
        curAmt = mState.getState(item)
        curAmt += amount
        mState.setState(item, curAmt)

    def getAmount(self, item):
        mState = self.state.getWorkflowState(self.scope)
        return mState.getState(item)

    def setAmount(self, item, amount):
        mState = self.state.getWorkflowState(self.scope)
        mState.setState(item, amount)
