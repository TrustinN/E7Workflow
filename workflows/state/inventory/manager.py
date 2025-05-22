from enum import Enum

from app import GlobalState
from workflows.state.state import StateManager


class InventoryManager(StateManager):

    def __init__(self, scope, items: Enum):
        super().__init__(scope)
        self.items = items

    def initState(self, state: GlobalState):
        super().initState(state)
        mState = state.getWorkflowState(self.scope)
        for item in self.items:
            mState.setState(item, 0)

    def subtractAmount(self, state: GlobalState, item, amount):
        assert amount >= 0

        mState = state.getWorkflowState(self.scope)
        curAmt = mState.getState(item)
        curAmt -= amount
        mState.setState(item, curAmt)

    def addAmount(self, state: GlobalState, item, amount):
        assert amount >= 0

        mState = state.getWorkflowState(self.scope)
        curAmt = mState.getState(item)
        curAmt += amount
        mState.setState(item, curAmt)

    def getAmount(self, state: GlobalState, item):
        mState = state.getWorkflowState(self.scope)
        return mState.getState(item)

    def setAmount(self, state: GlobalState, item, amount):
        mState = state.getWorkflowState(self.scope)
        mState.setState(item, amount)
