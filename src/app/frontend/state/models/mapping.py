from .model import Model


class MappingModel(Model):
    def __init__(self):
        super().__init__()

        self.data = {}

    def set(self, key, value):
        self.data[key] = value

    def get(self, key):
        return self.data[key]

    def delete(self, key):
        self.data.pop(key)

    def clear(self):
        self.data = {}

    def serialize(self):
        return self.data

    def deserialize(self, state):
        self.data = state
