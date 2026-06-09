from PyQt5.QtCore import QObject, pyqtSignal

from src.app.frontend.events import Node


class SelectionModel(QObject):
    selected_ = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.prevSelected = None
        self.selected = None

    def setSelected(self, id):
        self.prevSelected = self.selected
        self.selected = id
        self.selected_.emit(id)

    def getSelected(self):
        return self.selected

    def hasSelected(self):
        return self.setSelected is not None

    def getPrevSelected(self):
        return self.prevSelected

    def clearSelection(self):
        self.prevSelected = self.selected
        self.selected = None
        self.selected_.emit(None)

    def reset(self):
        self.selected = None
        self.prevSelected = None
        self.selected_.emit(None)


#
# class SelectionNode(Node):
#     def __init__(self, model: SelectionModel):
#         super().__init__()
#         self.model = model
#
#         self.subscribe("/Selection", self.onSelection)
#         self.subscribe("/App/Reset", self.resetSelection)
#
#     def onSelection(self, data):
#         self.model.setSelected(data["id"])
#
#     def resetSelection(self, data):
#         self.model.reset()
