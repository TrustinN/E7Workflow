import json

from .model import GraphModel


class GraphModelSerializer:
    def __init__(self):
        pass

    def export(self, model: GraphModel, path: str):
        state = model.serialize()
        with open(path, "w") as f:
            json.dump(state, f, indent=4)

    def restore(self, path: str):
        with open(path, "r") as f:
            return json.load(f)
