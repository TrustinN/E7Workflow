import json

from nanoid import generate

from .model import WorkspaceModel, WorkspaceSchema


class WorkspaceManager:
    def __init__(self, model: WorkspaceModel):
        self.model = model

    def createWorkspace(self, **kwargs) -> str:
        id = generate()

        schema = WorkspaceSchema(id=id, **kwargs)
        self.model.addItem(id, schema)
        return id

    def getWorkspace(self, id) -> WorkspaceSchema:
        return self.model.getItem(id)

    def deleteWorkspace(self, id):
        if id == self.model.rootIndex():
            return
        self.model.removeItem(id)

    def saveModel(self, file: str):
        state = self.model.toData()
        with open(file, "w") as f:
            json.dump(state, f, indent=4)

    def resetModel(self):
        self.model.clear()

    def loadModel(self, file: str):
        with open(file, "r") as f:
            state = json.load(f)

            self.model.fromData(state)
