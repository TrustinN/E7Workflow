import os

from src.app.frontend.events import Node
from src.app.frontend.models import GraphModel, Serializer
from src.app.frontend.state import SelectionModel

from .widget import RunnerButtons


class RunnerNode(Node):
    def __init__(
        self,
        model: GraphModel,
        selectionModel: SelectionModel,
        buttons: RunnerButtons,
    ):
        super().__init__()
        self.model = model
        self.selectionModel = selectionModel
        self.serializer = Serializer()

        self.modelFile = "runner_data.json"

        self.subscribe("/WS Component/WSCreated", self.createNode)
        self.subscribe("/Graph/EdgeCreated", self.createEdge)
        self.subscribe("/App/Reset", self.resetState)
        self.subscribe("/App/Export", self.runnerExport)
        self.subscribe("/App/Import", self.runnerImport)

        self.buttons = buttons

        self.buttons.executeBtn.clicked.connect(self.executeRunner)

    def createNode(self, data):
        self.model.createNode(data["id"], {})

    def createEdge(self, data):
        self.model.createEdge(data["id1"], data["id2"], {})

    def executeRunner(self):
        pass

    def runnerExport(self, data):
        path = data["path"]

        modelPath = os.path.join(path, self.modelFile)
        self.serializer.export(self.model, modelPath)

    def runnerImport(self, data):
        path = data["path"]

        modelPath = os.path.join(path, self.modelFile)
        modelState = self.serializer.restore(modelPath)
        self.model.deserialize(modelState)

    def resetState(self):
        pass
