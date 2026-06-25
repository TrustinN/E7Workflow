import json

from nanoid import generate

from src.app.components.workspace.model import WorkspaceSchema

from .model import EdgeSchema, GraphModel, NodeSchema


class GraphManager:
    def __init__(self, model: GraphModel):
        self.model = model

    def createNode(self, schema: WorkspaceSchema) -> str:
        id = schema.id
        schema = NodeSchema(
            id=id,
            name=schema.name,
            group=schema.grouping,
            parent=schema.parent,
        )

        self.model.addNode(id, schema)
        return id

    def createEdge(self, source: str, target: str) -> str:
        id = generate()

        schema = EdgeSchema(id=id, source=source, target=target)
        self.model.addEdge(id, schema)
        return id

    def saveModel(self, file):
        state = self.model.toData()
        with open(file, "w") as f:
            json.dump(state, f, indent=4)

    def resetModel(self):
        self.model.clear()

    def loadModel(self, file):
        with open(file, "r") as f:
            state = json.load(f)
            self.model.fromData(state)
